from collections import defaultdict, namedtuple

from dagster import check
from dagster.core.definitions.container import IContainSolids
from dagster.core.definitions.dependency import Solid, SolidInputHandle
from dagster.serdes import whitelist_for_serdes


def build_solid_invocation_snap(icontains_solids, solid):
    check.inst_param(solid, 'solid', Solid)
    check.inst_param(icontains_solids, 'icontains_solids', IContainSolids)
    dep_structure = icontains_solids.dependency_structure

    input_def_snaps = []

    input_to_outputs_map = dep_structure.input_to_upstream_outputs_for_solid(solid.name)

    for input_def in solid.definition.input_defs:
        input_handle = SolidInputHandle(solid, input_def)
        input_def_snaps.append(
            InputDependencySnap(
                input_def.name,
                upstream_output_snaps=[
                    OutputHandleSnap(oh.solid.name, oh.output_def.name)
                    for oh in input_to_outputs_map.get(input_handle, [])
                ],
            )
        )

    return SolidInvocationSnap(
        solid_name=solid.name,
        solid_def_name=solid.definition.name,
        tags=solid.tags,
        input_dep_snaps=input_def_snaps,
    )


def build_dep_structure_snapshot_from_icontains_solids(icontains_solids):
    check.inst_param(icontains_solids, 'icontains_solids', IContainSolids)
    return DependencyStructureSnapshot(
        solid_invocation_snaps=[
            build_solid_invocation_snap(icontains_solids, solid)
            for solid in icontains_solids.solids
        ]
    )


@whitelist_for_serdes
class DependencyStructureSnapshot(
    namedtuple('_DependencyStructureSnapshot', 'solid_invocation_snaps')
):
    def __new__(cls, solid_invocation_snaps):
        return super(DependencyStructureSnapshot, cls).__new__(
            cls,
            check.list_param(
                solid_invocation_snaps, 'solid_invocation_snaps', of_type=SolidInvocationSnap
            ),
        )


# Not actually serialized. Used within the dependency index
class InputHandle(namedtuple('_InputHandle', 'solid_def_name, solid_name input_name')):
    def __new__(cls, solid_def_name, solid_name, input_name):
        return super(InputHandle, cls).__new__(
            cls,
            solid_def_name=check.str_param(solid_def_name, 'solid_def_name'),
            solid_name=check.str_param(solid_name, 'solid_name'),
            input_name=check.str_param(input_name, 'input_name'),
        )


# This class contains all the dependency information
# for a given "level" in a pipeline. So either the pipelines
# or within a composite solid
class DependencyStructureIndex:
    def __init__(self, dep_structure_snapshot):
        check.inst_param(
            dep_structure_snapshot, 'dep_structure_snapshot', DependencyStructureSnapshot
        )
        self._invocations_dict = {
            si.solid_name: si for si in dep_structure_snapshot.solid_invocation_snaps
        }
        self._output_to_upstream_index = self._build_index(
            dep_structure_snapshot.solid_invocation_snaps
        )

    def _build_index(self, solid_invocation_snaps):
        output_to_upstream_index = defaultdict(lambda: defaultdict(list))
        for invocation in solid_invocation_snaps:
            for input_dep_snap in invocation.input_dep_snaps:
                for output_dep_snap in input_dep_snap.upstream_output_snaps:
                    output_to_upstream_index[output_dep_snap.solid_name][
                        output_dep_snap.output_name
                    ].append(
                        InputHandle(
                            solid_def_name=invocation.solid_def_name,
                            solid_name=invocation.solid_name,
                            input_name=input_dep_snap.input_name,
                        )
                    )

        return output_to_upstream_index

    @property
    def solid_invocation_names(self):
        return list(self._invocations_dict.keys())

    @property
    def solid_invocations(self):
        return list(self._invocations_dict.values())

    def get_invocation(self, solid_name):
        check.str_param(solid_name, 'solid_name')
        return self._invocations_dict[solid_name]

    def get_upstream_outputs(self, solid_name, input_name):
        check.str_param(solid_name, 'solid_name')
        check.str_param(input_name, 'input_name')

        for input_dep_snap in self.get_invocation(solid_name).input_dep_snaps:
            if input_dep_snap.input_name == input_name:
                return input_dep_snap.upstream_output_snaps

        check.failed(
            'Input {input_name} not found for solid {solid_name}'.format(
                input_name=input_name, solid_name=solid_name,
            )
        )

    def get_upstream_output(self, solid_name, input_name):
        check.str_param(solid_name, 'solid_name')
        check.str_param(input_name, 'input_name')

        outputs = self.get_upstream_outputs(solid_name, input_name)
        check.invariant(len(outputs) == 1)
        return outputs[0]

    def get_downstream_inputs(self, solid_name, output_name):
        check.str_param(solid_name, 'solid_name')
        check.str_param(output_name, 'output_name')
        return self._output_to_upstream_index[solid_name][output_name]


@whitelist_for_serdes
class OutputHandleSnap(namedtuple('_OutputHandleSnap', 'solid_name output_name')):
    def __new__(cls, solid_name, output_name):
        return super(OutputHandleSnap, cls).__new__(
            cls,
            solid_name=check.str_param(solid_name, 'solid_name'),
            output_name=check.str_param(output_name, 'output_name'),
        )


@whitelist_for_serdes
class InputDependencySnap(namedtuple('_InputDependencySnap', 'input_name upstream_output_snaps')):
    def __new__(cls, input_name, upstream_output_snaps):
        return super(InputDependencySnap, cls).__new__(
            cls,
            input_name=check.str_param(input_name, 'input_name'),
            upstream_output_snaps=check.list_param(
                upstream_output_snaps, 'upstream_output_snaps', of_type=OutputHandleSnap
            ),
        )


@whitelist_for_serdes
class SolidInvocationSnap(
    namedtuple('_SolidInvocationSnap', 'solid_name solid_def_name tags input_dep_snaps')
):
    def __new__(cls, solid_name, solid_def_name, tags, input_dep_snaps):
        return super(SolidInvocationSnap, cls).__new__(
            cls,
            solid_name=check.str_param(solid_name, 'solid_name'),
            solid_def_name=check.str_param(solid_def_name, 'solid_def_name'),
            tags=check.dict_param(tags, 'tags'),
            input_dep_snaps=check.list_param(
                input_dep_snaps, 'input_dep_snaps', of_type=InputDependencySnap
            ),
        )
