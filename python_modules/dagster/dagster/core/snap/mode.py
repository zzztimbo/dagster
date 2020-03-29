# Contains mode, resources, loggers
from collections import namedtuple

from dagster import check
from dagster.core.definitions import LoggerDefinition, ModeDefinition, ResourceDefinition
from dagster.serdes import whitelist_for_serdes

from .config_types import ConfigFieldSnap, snap_from_field


def build_mode_def_snap(mode_def):
    check.inst_param(mode_def, 'mode_def', ModeDefinition)

    return ModeDefSnap(
        name=mode_def.name,
        description=mode_def.description,
        resource_def_snaps=sorted(
            [build_resource_def_snap(name, rd) for name, rd in mode_def.resource_defs.items()],
            key=lambda item: item.name,
        ),
        logger_def_snaps=sorted(
            [build_logger_def_snap(name, ld) for name, ld in mode_def.loggers.items()],
            key=lambda item: item.name,
        ),
    )


@whitelist_for_serdes
class ModeDefSnap(
    namedtuple('_ModeDefSnap', 'name description resource_def_snaps logger_def_snaps')
):
    def __new__(cls, name, description, resource_def_snaps, logger_def_snaps):
        return super(ModeDefSnap, cls).__new__(
            cls,
            name=check.str_param(name, 'name'),
            description=check.opt_str_param(description, 'description'),
            resource_def_snaps=check.list_param(
                resource_def_snaps, 'resource_def_snaps', of_type=ResourceDefSnap
            ),
            logger_def_snaps=check.list_param(
                logger_def_snaps, 'logger_def_snaps', of_type=LoggerDefSnap
            ),
        )


def build_resource_def_snap(name, resource_def):
    check.str_param(name, 'name')
    check.inst_param(resource_def, 'resource_def', ResourceDefinition)
    return ResourceDefSnap(
        name=name,
        description=resource_def.description,
        config_field_snap=snap_from_field('config', resource_def.config_field)
        if resource_def.config_field
        else None,
    )


@whitelist_for_serdes
class ResourceDefSnap(namedtuple('_ResourceDefSnap', 'name description config_field_snap')):
    def __new__(cls, name, description, config_field_snap):
        return super(ResourceDefSnap, cls).__new__(
            cls,
            name=check.str_param(name, 'name'),
            description=check.opt_str_param(description, 'description'),
            config_field_snap=check.opt_inst_param(
                config_field_snap, 'config_field_snap', ConfigFieldSnap
            ),
        )


def build_logger_def_snap(name, logger_def):
    check.str_param(name, 'name')
    check.inst_param(logger_def, 'logger_def', LoggerDefinition)
    return LoggerDefSnap(
        name=name,
        description=logger_def.description,
        config_field_snap=snap_from_field('config', logger_def.config_field)
        if logger_def.config_field
        else None,
    )


@whitelist_for_serdes
class LoggerDefSnap(namedtuple('_LoggerDefSnap', 'name description config_field_snap')):
    def __new__(cls, name, description, config_field_snap):
        return super(LoggerDefSnap, cls).__new__(
            cls,
            name=check.str_param(name, 'name'),
            description=check.opt_str_param(description, 'description'),
            config_field_snap=check.opt_inst_param(
                config_field_snap, 'config_field_snap', ConfigFieldSnap
            ),
        )
