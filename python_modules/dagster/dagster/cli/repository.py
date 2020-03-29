import os
import sys

import click

from dagster import RepositoryDefinition
from dagster.cli.load_handle import handle_for_repo_cli_args
from dagster.cli.pipeline import repository_target_argument
from dagster.core.serdes import serialize_dagster_namedtuple
from dagster.core.snap.pipeline_snapshot import PipelineSnapshot
from dagster.core.snap.repository_snapshot import RepositorySnapshot


def create_repository_cli_group():
    group = click.Group(name='repository')
    group.add_command(snapshot_command)
    return group


@click.command(
    name='snapshot',
    help='Snapshot the given repository definition as a pickle file and load into target.',
)
@click.argument('pickle_target', type=click.Path())
@repository_target_argument
def snapshot_command(pickle_target, **kwargs):
    handle = handle_for_repo_cli_args(kwargs)

    # add the path for the cwd so imports in dynamically loaded code work correctly
    sys.path.append(os.getcwd())

    definition = handle.entrypoint.perform_load()
    snapshot = (
        RepositorySnapshot.from_repository_definition(definition)
        if isinstance(definition, RepositoryDefinition)
        else PipelineSnapshot.from_pipeline_def(definition)
    )

    with open(os.path.abspath(pickle_target), 'w+') as fp:
        fp.write(serialize_dagster_namedtuple(snapshot))


repository_cli = create_repository_cli_group()
