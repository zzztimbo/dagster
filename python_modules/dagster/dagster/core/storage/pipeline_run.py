from collections import namedtuple
from enum import Enum

from dagster import check
from dagster.core.execution.config import IRunConfig
from dagster.serdes import whitelist_for_serdes

from .tags import BACKFILL_ID_TAG, PARTITION_NAME_TAG, PARTITION_SET_TAG, SCHEDULE_NAME_TAG


@whitelist_for_serdes
class PipelineRunStatus(Enum):
    NOT_STARTED = 'NOT_STARTED'
    MANAGED = 'MANAGED'
    STARTED = 'STARTED'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'


@whitelist_for_serdes
class PipelineRunStatsSnapshot(
    namedtuple(
        '_PipelineRunStatsSnapshot',
        (
            'run_id steps_succeeded steps_failed materializations '
            'expectations start_time end_time'
        ),
    )
):
    def __new__(
        cls,
        run_id,
        steps_succeeded,
        steps_failed,
        materializations,
        expectations,
        start_time,
        end_time,
    ):
        return super(PipelineRunStatsSnapshot, cls).__new__(
            cls,
            run_id=check.str_param(run_id, 'run_id'),
            steps_succeeded=check.int_param(steps_succeeded, 'steps_succeeded'),
            steps_failed=check.int_param(steps_failed, 'steps_failed'),
            materializations=check.int_param(materializations, 'materializations'),
            expectations=check.int_param(expectations, 'expectations'),
            start_time=check.opt_float_param(start_time, 'start_time'),
            end_time=check.opt_float_param(end_time, 'end_time'),
        )


@whitelist_for_serdes
class PipelineRun(
    namedtuple(
        '_PipelineRun',
        (
            'pipeline_name run_id environment_dict mode selector '
            'step_keys_to_execute status tags previous_run_id'
        ),
    ),
    IRunConfig,
):
    '''Serializable internal representation of a pipeline run, as stored in a
    :py:class:`~dagster.core.storage.runs.RunStorage`.
    '''

    # serdes log
    # * removed reexecution_config - serdes logic expected to strip unknown keys so no need to preserve
    #
    def __new__(
        cls,
        pipeline_name,
        run_id,
        environment_dict,
        mode,
        selector=None,
        step_keys_to_execute=None,
        status=None,
        tags=None,
        previous_run_id=None,
    ):
        from dagster.core.definitions.pipeline import ExecutionSelector

        tags = check.opt_dict_param(tags, 'tags', key_type=str)
        selector = check.opt_inst_param(selector, 'selector', ExecutionSelector)
        if not selector:
            selector = ExecutionSelector(pipeline_name)

        if not status:
            status = PipelineRunStatus.NOT_STARTED

        return super(PipelineRun, cls).__new__(
            cls,
            pipeline_name=check.str_param(pipeline_name, 'pipeline_name'),
            run_id=check.str_param(run_id, 'run_id'),
            environment_dict=check.opt_dict_param(
                environment_dict, 'environment_dict', key_type=str
            ),
            mode=check.str_param(mode, 'mode'),
            selector=selector,
            step_keys_to_execute=None
            if step_keys_to_execute is None
            else check.list_param(step_keys_to_execute, 'step_keys_to_execute', of_type=str),
            status=status,
            tags=check.opt_dict_param(tags, 'tags', key_type=str),
            previous_run_id=check.opt_str_param(previous_run_id, 'previous_run_id'),
        )

    @staticmethod
    def create_empty_run(pipeline_name, run_id, environment_dict=None, tags=None):
        from dagster.core.definitions.pipeline import ExecutionSelector

        return PipelineRun(
            pipeline_name=pipeline_name,
            run_id=run_id,
            environment_dict=environment_dict,
            mode='default',
            selector=ExecutionSelector(pipeline_name),
            step_keys_to_execute=None,
            tags=tags,
            status=PipelineRunStatus.NOT_STARTED,
        )

    def run_with_status(self, status):
        return PipelineRun(
            pipeline_name=self.pipeline_name,
            run_id=self.run_id,
            environment_dict=self.environment_dict,
            mode=self.mode,
            selector=self.selector,
            step_keys_to_execute=self.step_keys_to_execute,
            tags=self.tags,
            status=status,
            previous_run_id=self.previous_run_id,
        )

    @property
    def is_finished(self):
        return self.status == PipelineRunStatus.SUCCESS or self.status == PipelineRunStatus.FAILURE

    @staticmethod
    def tags_for_schedule(schedule):
        return {SCHEDULE_NAME_TAG: schedule.name}

    @staticmethod
    def tags_for_backfill_id(backfill_id):
        return {BACKFILL_ID_TAG: backfill_id}

    @staticmethod
    def tags_for_partition_set(partition_set, partition):
        return {PARTITION_NAME_TAG: partition.name, PARTITION_SET_TAG: partition_set.name}


@whitelist_for_serdes
class PipelineRunsFilter(namedtuple('_PipelineRunsFilter', 'run_id tags pipeline_name status')):
    def __new__(cls, run_id=None, pipeline_name=None, status=None, tags=None):
        return super(PipelineRunsFilter, cls).__new__(
            cls,
            run_id=check.opt_str_param(run_id, 'run_id'),
            tags=check.opt_dict_param(tags, 'tags', key_type=str, value_type=str),
            pipeline_name=check.opt_str_param(pipeline_name, 'pipeline_name'),
            status=status,
        )

    def to_graphql_input(self):
        return {
            'runId': self.run_id,
            'tags': [{'key': k, 'value': v} for k, v in self.tags.items()],
            'pipelineName': self.pipeline_name,
            'status': self.status,
        }

    @staticmethod
    def for_schedule(schedule):
        return PipelineRunsFilter(tags=PipelineRun.tags_for_schedule(schedule))

    @staticmethod
    def for_partition(partition_set, partition):
        return PipelineRunsFilter(tags=PipelineRun.tags_for_partition_set(partition_set, partition))
