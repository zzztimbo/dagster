from __future__ import absolute_import

from dagster_graphql import dauphin

from dagster import PipelineDefinition, PresetDefinition, check
from dagster.core.snap.config_types import ConfigSchemaSnapshot
from dagster.core.snap.mode import LoggerDefSnap, ModeDefSnap, ResourceDefSnap
from dagster.core.snap.pipeline_snapshot import PipelineIndex
from dagster.core.storage.pipeline_run import PipelineRunsFilter
from dagster.seven import lru_cache

from .config_types import DauphinConfigTypeField
from .runtime_types import to_dauphin_dagster_type
from .solids import DauphinSolidContainer, build_dauphin_solid_handles, build_dauphin_solids


class DauphinPipelineReference(dauphin.Interface):
    '''This interface supports the case where we can look up a pipeline successfully in the
    repository available to the DagsterInstance/graphql context, as well as the case where we know
    that a pipeline exists/existed thanks to materialized data such as logs and run metadata, but
    where we can't look the concrete pipeline up.'''

    class Meta(object):
        name = 'PipelineReference'

    name = dauphin.NonNull(dauphin.String)


class DauphinUnknownPipeline(dauphin.ObjectType):
    class Meta(object):
        name = 'UnknownPipeline'
        interfaces = (DauphinPipelineReference,)

    name = dauphin.NonNull(dauphin.String)


class DauphinIPipelineSnapshotMixin(object):
    # Mixin this class to implement IPipelineSnapshot
    #
    # Graphene has some strange properties that make it so that you cannot
    # implement ABCs nor use properties in an overridable way. So the way
    # the mixin works is that the target classes have to have a method
    # get_pipeline_index()
    #
    def get_pipeline_index(self):

        raise NotImplementedError()

    name = dauphin.NonNull(dauphin.String)
    description = dauphin.String()
    runtime_types = dauphin.non_null_list('RuntimeType')
    solids = dauphin.non_null_list('Solid')
    runs = dauphin.non_null_list('PipelineRun')
    modes = dauphin.non_null_list('Mode')
    solid_handles = dauphin.Field(
        dauphin.non_null_list('SolidHandle'), parentHandleID=dauphin.String()
    )
    solid_handle = dauphin.Field(
        'SolidHandle', handleID=dauphin.Argument(dauphin.NonNull(dauphin.String)),
    )
    tags = dauphin.non_null_list('PipelineTag')

    def resolve_name(self, _):
        return self.get_pipeline_index().name

    def resolve_description(self, _):
        return self.get_pipeline_index().description

    def resolve_runtime_types(self, _graphene_info):
        # TODO yuhan rename runtime_type in schema
        pipeline_index = self.get_pipeline_index()
        return sorted(
            list(
                map(
                    lambda dt: to_dauphin_dagster_type(pipeline_index.pipeline_snapshot, dt.key),
                    [t for t in pipeline_index.get_dagster_type_snaps() if t.name],
                )
            ),
            key=lambda dagster_type: dagster_type.name,
        )

    def resolve_solids(self, _graphene_info):
        pipeline_index = self.get_pipeline_index()
        return build_dauphin_solids(pipeline_index, pipeline_index.dep_structure_index)

    def resolve_runs(self, graphene_info):
        return [
            graphene_info.schema.type_named('PipelineRun')(r)
            for r in graphene_info.context.instance.get_runs(
                filters=PipelineRunsFilter(pipeline_name=self.get_pipeline_index().name)
            )
        ]

    def resolve_modes(self, _):
        pipeline_snapshot = self.get_pipeline_index().pipeline_snapshot
        return [
            DauphinMode(pipeline_snapshot.config_schema_snapshot, mode_def_snap)
            for mode_def_snap in sorted(
                pipeline_snapshot.mode_def_snaps, key=lambda item: item.name
            )
        ]

    def resolve_solid_handle(self, _graphene_info, handleID):
        return _get_solid_handles(self.get_pipeline_index()).get(handleID)

    def resolve_solid_handles(self, _graphene_info, **kwargs):
        handles = _get_solid_handles(self.get_pipeline_index())
        parentHandleID = kwargs.get('parentHandleID')

        if parentHandleID == "":
            handles = {key: handle for key, handle in handles.items() if not handle.parent}
        elif parentHandleID is not None:
            handles = {
                key: handle
                for key, handle in handles.items()
                if handle.parent and handle.parent.handleID.to_string() == parentHandleID
            }

        return [handles[key] for key in sorted(handles)]

    def resolve_tags(self, graphene_info):
        return [
            graphene_info.schema.type_named('PipelineTag')(key=key, value=value)
            for key, value in self.get_pipeline_index().pipeline_snapshot.tags.items()
        ]


class DauphinIPipelineSnapshot(dauphin.Interface):
    class Meta(object):
        name = 'IPipelineSnapshot'

    name = dauphin.NonNull(dauphin.String)
    description = dauphin.String()
    runtime_types = dauphin.non_null_list('RuntimeType')
    solids = dauphin.non_null_list('Solid')
    runs = dauphin.non_null_list('PipelineRun')
    modes = dauphin.non_null_list('Mode')
    solid_handles = dauphin.Field(
        dauphin.non_null_list('SolidHandle'), parentHandleID=dauphin.String()
    )
    solid_handle = dauphin.Field(
        'SolidHandle', handleID=dauphin.Argument(dauphin.NonNull(dauphin.String)),
    )
    tags = dauphin.non_null_list('PipelineTag')


class DauphinPipeline(DauphinIPipelineSnapshotMixin, dauphin.ObjectType):
    class Meta(object):
        name = 'Pipeline'
        interfaces = (DauphinSolidContainer, DauphinPipelineReference, DauphinIPipelineSnapshot)

    presets = dauphin.non_null_list('PipelinePreset')

    def __init__(self, pipeline):
        self._pipeline = check.inst_param(pipeline, 'pipeline', PipelineDefinition)
        self._pipeline_index = self._pipeline.get_pipeline_index()

    def get_pipeline_index(self):
        return self._pipeline_index

    def resolve_presets(self, _graphene_info):
        return [
            DauphinPipelinePreset(preset, self._pipeline_index.name)
            for preset in sorted(self._pipeline.get_presets(), key=lambda item: item.name)
        ]


@lru_cache(maxsize=32)
def _get_solid_handles(pipeline_index):
    return {
        str(item.handleID): item
        for item in build_dauphin_solid_handles(pipeline_index, pipeline_index.dep_structure_index)
    }


class DauphinPipelineConnection(dauphin.ObjectType):
    class Meta(object):
        name = 'PipelineConnection'

    nodes = dauphin.non_null_list('Pipeline')


class DauphinResource(dauphin.ObjectType):
    class Meta(object):
        name = 'Resource'

    def __init__(self, config_schema_snapshot, resource_def_snap):
        self._config_schema_snapshot = check.inst_param(
            config_schema_snapshot, 'config_schema_snapshot', ConfigSchemaSnapshot
        )
        self._resource_dep_snap = check.inst_param(
            resource_def_snap, 'resource_def_snap', ResourceDefSnap
        )
        self.name = resource_def_snap.name
        self.description = resource_def_snap.description

    name = dauphin.NonNull(dauphin.String)
    description = dauphin.String()
    configField = dauphin.Field('ConfigTypeField')

    def resolve_configField(self, _):
        return (
            DauphinConfigTypeField(
                config_schema_snapshot=self._config_schema_snapshot,
                field_snap=self._resource_dep_snap.config_field_snap,
            )
            if self._resource_dep_snap.config_field_snap
            else None
        )


class DauphinLogger(dauphin.ObjectType):
    class Meta(object):
        name = 'Logger'

    def __init__(self, config_schema_snapshot, logger_def_snap):
        self._config_schema_snapshot = check.inst_param(
            config_schema_snapshot, 'config_schema_snapshot', ConfigSchemaSnapshot
        )
        self._logger_def_snap = check.inst_param(logger_def_snap, 'logger_def_snap', LoggerDefSnap)
        self.name = logger_def_snap.name
        self.description = logger_def_snap.description

    name = dauphin.NonNull(dauphin.String)
    description = dauphin.String()
    configField = dauphin.Field('ConfigTypeField')

    def resolve_configField(self, _):
        return (
            DauphinConfigTypeField(
                config_schema_snapshot=self._config_schema_snapshot,
                field_snap=self._logger_def_snap.config_field_snap,
            )
            if self._logger_def_snap.config_field_snap
            else None
        )


class DauphinMode(dauphin.ObjectType):
    def __init__(self, config_schema_snapshot, mode_def_snap):
        self._mode_def_snap = check.inst_param(mode_def_snap, 'mode_def_snap', ModeDefSnap)
        self._config_schema_snapshot = check.inst_param(
            config_schema_snapshot, 'config_schema_snapshot', ConfigSchemaSnapshot
        )

    class Meta(object):
        name = 'Mode'

    name = dauphin.NonNull(dauphin.String)
    description = dauphin.String()
    resources = dauphin.non_null_list('Resource')
    loggers = dauphin.non_null_list('Logger')

    def resolve_name(self, _graphene_info):
        return self._mode_def_snap.name

    def resolve_description(self, _graphene_info):
        return self._mode_def_snap.description

    def resolve_resources(self, _graphene_info):
        return [
            DauphinResource(self._config_schema_snapshot, resource_def_snap)
            for resource_def_snap in sorted(self._mode_def_snap.resource_def_snaps)
        ]

    def resolve_loggers(self, _graphene_info):
        return [
            DauphinLogger(self._config_schema_snapshot, logger_def_snap)
            for logger_def_snap in sorted(self._mode_def_snap.logger_def_snaps)
        ]


class DauphinMetadataItemDefinition(dauphin.ObjectType):
    class Meta(object):
        name = 'MetadataItemDefinition'

    key = dauphin.NonNull(dauphin.String)
    value = dauphin.NonNull(dauphin.String)


class DauphinPipelinePreset(dauphin.ObjectType):
    class Meta(object):
        name = 'PipelinePreset'

    name = dauphin.NonNull(dauphin.String)
    solidSubset = dauphin.List(dauphin.NonNull(dauphin.String))
    environmentConfigYaml = dauphin.NonNull(dauphin.String)
    mode = dauphin.NonNull(dauphin.String)

    def __init__(self, preset, pipeline_name):
        self._preset = check.inst_param(preset, 'preset', PresetDefinition)
        self._pipeline_name = check.str_param(pipeline_name, 'pipeline_name')

    def resolve_name(self, _graphene_info):
        return self._preset.name

    def resolve_solidSubset(self, _graphene_info):
        return self._preset.solid_subset

    def resolve_environmentConfigYaml(self, _graphene_info):
        yaml = self._preset.get_environment_yaml()
        return yaml if yaml else ''

    def resolve_mode(self, _graphene_info):
        return self._preset.mode


class DauphinPipelineSnapshot(DauphinIPipelineSnapshotMixin, dauphin.ObjectType):
    def __init__(self, pipeline_index):
        self._pipeline_index = check.inst_param(pipeline_index, 'pipeline_index', PipelineIndex)

    class Meta(object):
        name = 'PipelineSnapshot'
        interaces = (DauphinIPipelineSnapshot,)

    def get_pipeline_index(self):
        return self._pipeline_index
