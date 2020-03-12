import datetime
import time

from dagster import (
    Field,
    Int,
    Output,
    OutputDefinition,
    RepositoryDefinition,
    RetryRequested,
    String,
    pipeline,
    solid,
)
from dagster.core.definitions.pipeline import PipelineRunsFilter
from dagster.core.execution.plan.objects import StepOutputHandle

@solid(
    config={
        'pipeline_name': String,
        'solid_name': String,
        'output_name': String,
        'freshness': {
            'days': Field(Int, default_value=0, is_required=False),
            'seconds': Field(Int, default_value=0, is_required=False),
            'microseconds': Field(Int, default_value=0, is_required=False),
            'milliseconds': Field(Int, default_value=0, is_required=False),
            'minutes': Field(Int, default_value=0, is_required=False),
            'hours': Field(Int, default_value=0, is_required=False),
            'weeks': Field(Int, default_value=0, is_required=False),
        },
        'max_retries': Field(Int, default_value=3, is_required=False),
        'seconds_to_wait': Field(Int, default_value=10, is_required=False),
    },
    output_defs=[
        OutputDefinition(dagster_type=String)
    ]
)
def external_task_sensor(context):
    pipeline_name = context.solid_config['pipeline_name']
    max_retries = context.solid_config['max_retries']
    seconds_to_wait = context.solid_config['seconds_to_wait']
    freshness = datetime.timedelta(**(context.solid_config['freshness']))

    system_context = context._system_compute_execution_context
    instance = system_context.instance
    intermediates_manager = system_context.intermediates_manager

    step_output_handle = StepOutputHandle(
        context.solid_config['solid_name'] + '.compute', context.solid_config['output_name']
    )

    now = time.time()

    runs = instance.get_runs(
        filters=PipelineRunsFilter(run_id=None, tags=None, pipeline_name=pipeline_name, status=None)
    )
    for run in runs:
        run_id = run.run_id
        start_time = instance.get_run_stats(run_id).start_time
        if not start_time:
            continue
        td = datetime.timedelta(seconds=now-start_time)
        if not td < freshness:
            break  # This is relying on the autoincrement
        # FIXME if the step output handle matchs, this could overwrite
        intermediates_manager.copy_intermediate_from_prev_run(context, run_id, step_output_handle)
        res = intermediates_manager.get_intermediate(
            system_context,
            step_output_handle=step_output_handle,
            dagster_type=context.solid_def.output_defs[0].dagster_type
        )
        yield Output(res.obj, 'result')
        return

    raise RetryRequested(max_retries=max_retries, seconds_to_wait=seconds_to_wait)


@solid(config={
    'delay': Int,
    'return_value': String
})
def waiter(context):
    start = time.time()
    delay = context.solid_config['delay']
    while True:
        if time.time() - start > delay:
            break
    return context.solid_config['return_value']


@pipeline
def waiting_pipeline():
    waiter()

@pipeline
def xdag_pipeline():
    external_task_sensor()

def xdag_repository():
    return RepositoryDefinition(
    'xdag_repository',
    pipeline_dict={
        'waiting_pipeline': lambda: waiting_pipeline,
        'xdag_pipeline': lambda: xdag_pipeline,
    }
)
