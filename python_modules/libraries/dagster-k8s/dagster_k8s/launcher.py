from dagster_graphql.client.util import execution_params_from_pipeline_run
from kubernetes import client, config

from dagster import Field, Noneable
from dagster import __version__ as dagster_version
from dagster import check
from dagster.core.instance import DagsterInstance
from dagster.core.launcher import RunLauncher
from dagster.core.storage.pipeline_run import PipelineRun
from dagster.serdes import ConfigurableClass, ConfigurableClassData
from dagster.seven import json

BACKOFF_LIMIT = 4

TTL_SECONDS_AFTER_FINISHED = 100


class K8sRunLauncher(RunLauncher, ConfigurableClass):
    '''RunLauncher that starts a Kubernetes Job for each pipeline run.

    Encapsulates each pipeline run in a separate, isolated invocation of ``dagster-graphql``.

    You may configure a Dagster instance to use this RunLauncher by adding a section to your
    ``dagster.yaml`` like the following:

    .. code-block:: yaml

        run_launcher:
            module: dagster_k8s.launcher
            class: K8sRunLauncher
            config:
                service_account_name: job_runner_service_account
                job_image: my_project/dagster_image:latest
                instance_config_map: dagster-instance
                postgres_password_secret: dagster-postgresql-secret

    As always when using a :py:class:`~dagster.serdes.ConfigurableClass`, the values
    under the ``config`` key of this YAML block will be passed to the constructor. The full list
    of acceptable values is given below by the constructor args.

    Args:
        service_account_name (str): The name of the Kubernetes service account under which to run
            the Job.
        job_image (str): The ``name`` of the image to use for the Job's Dagster container. This
            image will be run with the command
            ``dagster-graphql -p startPipelineExecution -v {executionParams}``.
        instance_config_map (str): The ``name`` of an existing Volume to mount into the pod in
            order to provide a ConfigMap for the Dagster instance. This Volume should contain a
            ``dagster.yaml`` with appropriate values for run storage, event log storage, etc.
        postgres_password_secret (str): The name of the Kubernetes Secret where the postgres
            password can be retrieved. Will be mounted and supplied as an environment variable to
            the Job Pod.
        dagster_home (str): The location of DAGSTER_HOME in the Job container; this is where the
            ``dagster.yaml`` file will be mounted from the instance ConfigMap specified above.
        load_kubeconfig (Optional[bool]): If ``True``, will load k8s config from the file specified
            in ``kubeconfig_file`` (using ``kubernetes.config.load_kube_config``). Set this value
            if you are running the launcher outside of a k8s cluster (e.g., in test) or you intend
            to target another cluster than that in which the launcher is running. If ``False``, we
            assume the launcher is running within the target cluster and load config using
            ``kubernetes.config.load_incluster_config``. Default: ``False``.
        kubeconfig_file (Optional[str]): The kubeconfig file from which to load config. Required if
            ``load_kubeconfig`` is ``True``.
        image_pull_secrets (Optional[List[Dict[str, str]]]): Optionally, a list of dicts, each of
            which corresponds to a Kubernetes ``LocalObjectReference`` (e.g.,
            ``{'name': 'myRegistryName'}``). This allows you to specify the ```imagePullSecrets`` on
            a pod basis. Typically, these will be provided through the service account, when needed,
            and you will not need to pass this argument.
            See:
            https://kubernetes.io/docs/concepts/containers/images/#specifying-imagepullsecrets-on-a-pod
            and https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.17/#podspec-v1-core.
        image_pull_policy (Optional[str]): Allows the image pull policy to be overridden, e.g. to
            facilitate local testing with `kind <https://kind.sigs.k8s.io/>`_. Default:
            ``"Always"``. See: https://kubernetes.io/docs/concepts/containers/images/#updating-images.
        job_namespace (Optional[str]): The namespace into which to launch new jobs. Note that any
            other Kubernetes resources the Job requires (such as the service account) must be
            present in this namespace. Default: ``"default"``
        env_config_maps (Optional[List[str]]): A list of custom ConfigMapEnvSource names from which to
            draw environment variables (using ``envFrom``) for the Job. Default: ``[]``. See:
        https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/#define-an-environment-variable-for-a-container
        env_secrets (Optional[List[str]]): A list of custom Secret names from which to
            draw environment variables (using ``envFrom``) for the Job. Default: ``[]``. See:
        https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/#configure-all-key-value-pairs-in-a-secret-as-container-environment-variables
    '''

    def __init__(
        self,
        service_account_name,
        job_image,
        instance_config_map,
        postgres_password_secret,
        dagster_home,
        image_pull_policy='Always',
        image_pull_secrets=None,
        load_kubeconfig=False,
        kubeconfig_file=None,
        inst_data=None,
        job_namespace='default',
        env_config_maps=None,
        env_secrets=None,
    ):
        self._inst_data = check.opt_inst_param(inst_data, 'inst_data', ConfigurableClassData)
        self.job_image = check.str_param(job_image, 'job_image')
        self.instance_config_map = check.str_param(instance_config_map, 'instance_config_map')
        self.postgres_password_secret = check.str_param(
            postgres_password_secret, 'postgres_password_secret'
        )
        self.dagster_home = check.str_param(dagster_home, 'dagster_home')
        self.image_pull_secrets = check.opt_list_param(image_pull_secrets, 'image_pull_secrets')
        self.image_pull_policy = check.str_param(image_pull_policy, 'image_pull_policy')
        self.service_account_name = check.str_param(service_account_name, 'service_account_name')
        self.job_namespace = check.str_param(job_namespace, 'job_namespace')
        self._env_config_maps = check.opt_list_param(
            env_config_maps, 'env_config_maps', of_type=str
        )
        self._env_secrets = check.opt_list_param(env_secrets, 'env_secrets', of_type=str)
        check.bool_param(load_kubeconfig, 'load_kubeconfig')
        if load_kubeconfig:
            check.str_param(kubeconfig_file, 'kubeconfig_file')
        else:
            check.invariant(
                kubeconfig_file is None, '`kubeconfig_file` is set but `load_kubeconfig` is True.'
            )

        if load_kubeconfig:
            config.load_kube_config(kubeconfig_file)
        else:
            config.load_incluster_config()

        self._kube_api = client.BatchV1Api()

    @classmethod
    def config_type(cls):
        return {
            'service_account_name': str,
            'job_image': str,
            'instance_config_map': str,
            'postgres_password_secret': str,
            'dagster_home': str,
            'image_pull_secrets': Field(Noneable(list), is_required=False),
            'image_pull_policy': Field(str, is_required=False, default_value='Always'),
            'job_namespace': str,
            'env_config_maps': Field(Noneable(list), is_required=False),
            'env_secrets': Field(Noneable(list), is_required=False),
            'load_kubeconfig': Field(bool, is_required=False, default_value=False),
            'kubeconfig_file': Field(Noneable(str), is_required=False, default_value=None),
        }

    @classmethod
    def from_config_value(cls, inst_data, config_value):
        return cls(inst_data=inst_data, **config_value)

    @property
    def inst_data(self):
        return self._inst_data

    @property
    def env_from_sources(self):
        '''This constructs a list of env_from sources. Along with a default base environment
        config map which we always load, the ConfigMaps and Secrets specified via
        config_map_env_froms and secret_env_froms will be pulled into the job construction here.
        '''
        config_maps = [
            client.V1EnvFromSource(config_map_ref=client.V1ConfigMapEnvSource(name=config_map))
            for config_map in self._env_config_maps
        ]

        secrets = [
            client.V1EnvFromSource(secret_ref=client.V1SecretEnvSource(name=secret))
            for secret in self._env_secrets
        ]

        return config_maps + secrets

    def construct_job(self, run):
        check.inst_param(run, 'run', PipelineRun)

        dagster_labels = {
            'app.kubernetes.io/name': 'dagster',
            'app.kubernetes.io/instance': 'dagster',
            'app.kubernetes.io/version': dagster_version,
        }

        execution_params = execution_params_from_pipeline_run(run)

        job_container = client.V1Container(
            name='dagster-job-%s' % run.run_id,
            image=self.job_image,
            command=['dagster-graphql'],
            args=[
                '-p',
                'startPipelineExecution',
                '-v',
                json.dumps({'executionParams': execution_params.to_graphql_input()}),
            ],
            image_pull_policy=self.image_pull_policy,
            env=[
                client.V1EnvVar(
                    name='DAGSTER_PG_PASSWORD',
                    value_from=client.V1EnvVarSource(
                        secret_key_ref=client.V1SecretKeySelector(
                            name=self.postgres_password_secret, key='postgresql-password'
                        )
                    ),
                ),
            ],
            env_from=self.env_from_sources,
            volume_mounts=[
                client.V1VolumeMount(
                    name='dagster-instance',
                    mount_path='{dagster_home}/dagster.yaml'.format(dagster_home=self.dagster_home),
                    sub_path='dagster.yaml',
                )
            ],
        )

        config_map_volume = client.V1Volume(
            name='dagster-instance',
            config_map=client.V1ConfigMapVolumeSource(name=self.instance_config_map),
        )

        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                name='dagster-job-pod-%s' % run.run_id, labels=dagster_labels,
            ),
            spec=client.V1PodSpec(
                image_pull_secrets=self.image_pull_secrets,
                service_account_name=self.service_account_name,
                restart_policy='Never',
                containers=[job_container],
                volumes=[config_map_volume],
            ),
        )

        job = client.V1Job(
            api_version='batch/v1',
            kind='Job',
            metadata=client.V1ObjectMeta(name='dagster-job-%s' % run.run_id, labels=dagster_labels),
            spec=client.V1JobSpec(
                template=template,
                backoff_limit=BACKOFF_LIMIT,
                ttl_seconds_after_finished=TTL_SECONDS_AFTER_FINISHED,
            ),
        )
        return job

    def launch_run(self, instance, run):
        check.inst_param(run, 'run', PipelineRun)
        check.inst_param(instance, 'instance', DagsterInstance)

        instance.create_run(run)
        job = self.construct_job(run)
        api_response = self._kube_api.create_namespaced_job(body=job, namespace=self.job_namespace)
        # FIXME add an event here
        print("Job created. status='%s'" % str(api_response.status))
        return run
