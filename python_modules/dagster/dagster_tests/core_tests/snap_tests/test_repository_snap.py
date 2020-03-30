from dagster import RepositoryDefinition, pipeline, solid
from dagster.core.snap.repository_snapshot import RepositorySnapshot
from dagster.serdes import serialize_dagster_namedtuple


def test_repository_snap_all_props(snapshot):
    @solid
    def noop_solid(_):
        pass

    @pipeline
    def noop_pipeline():
        noop_solid()

    repo = RepositoryDefinition(name='noop_repo', pipeline_defs=[noop_pipeline])
    repo_snap = RepositorySnapshot.from_repository_definition(repo)

    snapshot.assert_match(serialize_dagster_namedtuple(repo_snap))


def test_repository_snap_empty(snapshot):
    repo = RepositoryDefinition(name='empty_repo', pipeline_defs=[])
    repo_snap = RepositorySnapshot.from_repository_definition(repo)
    snapshot.assert_match(serialize_dagster_namedtuple(repo_snap))
