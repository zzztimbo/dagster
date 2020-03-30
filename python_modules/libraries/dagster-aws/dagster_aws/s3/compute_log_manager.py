import os
from contextlib import contextmanager

from dagster import Field, check, seven
from dagster.core.storage.compute_log_manager import (
    MAX_BYTES_FILE_READ,
    ComputeIOType,
    ComputeLogFileData,
    ComputeLogManager,
)
from dagster.core.storage.local_compute_log_manager import IO_TYPE_EXTENSION, LocalComputeLogManager
from dagster.serdes import ConfigurableClass, ConfigurableClassData
from dagster.utils import ensure_dir, ensure_file

from .utils import create_s3_session


class S3ComputeLogManager(ComputeLogManager, ConfigurableClass):
    '''Logs solid compute function stdout and stderr to S3.

    Users should not instantiate this class directly. Instead, use a YAML block in ``dagster.yaml``
    such as the following:

    .. code-block:: YAML

        compute_log_manager:
          module: dagster_aws.s3.compute_log_manager
          class: S3ComputeLogManager
          config:
            bucket: "mycorp-dagster-compute-logs"
            local_dir: "/tmp/cool"
            prefix: "dagster-test-"

    Args:
        bucket (str): The name of the s3 bucket to which to log.
        local_dir (Optional[str]): Path to the local directory in which to stage logs. Default:
            ``dagster.seven.get_system_temp_directory()``.
        prefix (Optional[str]): Prefix for the log file keys.
        inst_data (Optional[ConfigurableClassData]): Serializable representation of the compute
            log manager when newed up from config.
    '''

    def __init__(self, bucket, local_dir=None, inst_data=None, prefix='dagster'):
        self._s3_session = create_s3_session()
        self._s3_bucket = check.str_param(bucket, 'bucket')
        self._s3_prefix = check.str_param(prefix, 'prefix')
        self._download_urls = {}

        # proxy calls to local compute log manager (for subscriptions, etc)
        if not local_dir:
            local_dir = seven.get_system_temp_directory()

        self.local_manager = LocalComputeLogManager(local_dir)
        self._inst_data = check.opt_inst_param(inst_data, 'inst_data', ConfigurableClassData)

    @contextmanager
    def _watch_logs(self, pipeline_run, step_key=None):
        # proxy watching to the local compute log manager, interacting with the filesystem
        with self.local_manager._watch_logs(  # pylint: disable=protected-access
            pipeline_run, step_key
        ):
            yield

    @property
    def inst_data(self):
        return self._inst_data

    @classmethod
    def config_type(cls):
        return {
            'bucket': str,
            'local_dir': Field(str, is_required=False),
            'prefix': Field(str, is_required=False, default_value='dagster'),
        }

    @staticmethod
    def from_config_value(inst_data, config_value):
        return S3ComputeLogManager(inst_data=inst_data, **config_value)

    def get_local_path(self, run_id, key, io_type):
        return self.local_manager.get_local_path(run_id, key, io_type)

    def on_watch_start(self, pipeline_run, step_key):
        self.local_manager.on_watch_start(pipeline_run, step_key)

    def on_watch_finish(self, pipeline_run, step_key):
        self.local_manager.on_watch_finish(pipeline_run, step_key)
        key = self.local_manager.get_key(pipeline_run, step_key)
        self._upload_from_local(pipeline_run.run_id, key, ComputeIOType.STDOUT)
        self._upload_from_local(pipeline_run.run_id, key, ComputeIOType.STDERR)

    def is_watch_completed(self, run_id, key):
        return self.local_manager.is_watch_completed(run_id, key)

    def download_url(self, run_id, key, io_type):
        if not self.is_watch_completed(run_id, key):
            return self.local_manager.download_url(run_id, key, io_type)
        key = self._bucket_key(run_id, key, io_type)
        if key in self._download_urls:
            return self._download_urls[key]
        url = self._s3_session.generate_presigned_url(
            ClientMethod='get_object', Params={'Bucket': self._s3_bucket, 'Key': key}
        )
        self._download_urls[key] = url
        return url

    def read_logs_file(self, run_id, key, io_type, cursor=0, max_bytes=MAX_BYTES_FILE_READ):
        if self._should_download(run_id, key, io_type):
            self._download_to_local(run_id, key, io_type)
        data = self.local_manager.read_logs_file(run_id, key, io_type, cursor, max_bytes)
        return self._from_local_file_data(run_id, key, io_type, data)

    def on_subscribe(self, subscription):
        self.local_manager.on_subscribe(subscription)

    def _should_download(self, run_id, key, io_type):
        local_path = self.get_local_path(run_id, key, io_type)
        if os.path.exists(local_path):
            return False
        s3_objects = self._s3_session.list_objects(
            Bucket=self._s3_bucket, Prefix=self._bucket_key(run_id, key, io_type)
        )
        return len(s3_objects) > 0

    def _from_local_file_data(self, run_id, key, io_type, local_file_data):
        is_complete = self.is_watch_completed(run_id, key)
        path = (
            's3://{}/{}'.format(self._s3_bucket, self._bucket_key(run_id, key, io_type))
            if is_complete
            else local_file_data.path
        )

        return ComputeLogFileData(
            path,
            local_file_data.data,
            local_file_data.cursor,
            local_file_data.size,
            self.download_url(run_id, key, io_type),
        )

    def _upload_from_local(self, run_id, key, io_type):
        path = self.get_local_path(run_id, key, io_type)
        ensure_file(path)
        key = self._bucket_key(run_id, key, io_type)
        with open(path, 'rb') as data:
            self._s3_session.upload_fileobj(data, self._s3_bucket, key)

    def _download_to_local(self, run_id, key, io_type):
        path = self.get_local_path(run_id, key, io_type)
        ensure_dir(os.path.dirname(path))
        with open(path, 'wb') as fileobj:
            self._s3_session.download_fileobj(
                self._s3_bucket, self._bucket_key(run_id, key, io_type), fileobj
            )

    def _bucket_key(self, run_id, key, io_type):
        check.inst_param(io_type, 'io_type', ComputeIOType)
        extension = IO_TYPE_EXTENSION[io_type]
        paths = [
            self._s3_prefix,
            'storage',
            run_id,
            'compute_logs',
            '{}.{}'.format(key, extension),
        ]
        return '/'.join(paths)  # s3 path delimiter
