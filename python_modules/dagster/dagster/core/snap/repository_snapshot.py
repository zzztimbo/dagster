from collections import namedtuple

from dagster import RepositoryDefinition, check
from dagster.core.serdes import whitelist_for_serdes
from dagster.core.snap.pipeline_snapshot import PipelineSnapshot


@whitelist_for_serdes
class RepositorySnapshot(namedtuple('_RepositorySnapshot', 'name pipeline_snapshots')):
    def __new__(cls, name, pipeline_snapshots):
        return super(RepositorySnapshot, cls).__new__(
            cls,
            name=check.str_param(name, 'name'),
            pipeline_snapshots=check.list_param(
                pipeline_snapshots, 'pipeline_snapshots', of_type=PipelineSnapshot
            ),
        )

    @staticmethod
    def from_repository_definition(repository_definition):
        check.inst_param(repository_definition, 'repository_definition', RepositoryDefinition)
        return RepositorySnapshot(
            name=repository_definition.name,
            pipeline_snapshots=[
                PipelineSnapshot.from_pipeline_def(pipeline_definition)
                for pipeline_definition in repository_definition.get_all_pipelines()
            ],
        )
