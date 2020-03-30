from dagster import check
from dagster.builtins import BuiltinEnum
from dagster.core.errors import DagsterInvalidConfigError, DagsterInvalidDefinitionError
from dagster.utils.backcompat import canonicalize_backcompat_args
from dagster.utils.typing_api import is_typing_type

from .config_type import Array, ConfigAnyInstance, ConfigType
from .field_utils import FIELD_NO_DEFAULT_PROVIDED, all_optional_type


def _is_config_type_class(obj):
    return isinstance(obj, type) and issubclass(obj, ConfigType)


def helpful_list_error_string():
    return 'Please use a python list (e.g. [int]) or dagster.Array (e.g. Array(int)) instead.'


VALID_CONFIG_DESC = '''
1. A Python primitive type that resolve to dagster config
   types: int, float, bool, str.

2. A dagster config type: Int, Float, Bool, String, StringSource, Path, Any,
   Array, Noneable, Selector, Shape, Permissive, etc.

3. A bare python dictionary, which is wrapped in Shape. Any
   values in the dictionary get resolved by the same rules, recursively.

4. A bare python list of length one which itself is config type.
   Becomes Array with list element as an argument.
'''


def resolve_to_config_type(dagster_type):
    from .field_utils import convert_fields_to_dict_type

    # Short circuit if it's already a Config Type
    if isinstance(dagster_type, ConfigType):
        return dagster_type

    if isinstance(dagster_type, dict):
        return convert_fields_to_dict_type(dagster_type)

    if isinstance(dagster_type, list):
        if len(dagster_type) != 1:
            raise DagsterInvalidDefinitionError('Array specifications must only be of length 1')

        inner_type = resolve_to_config_type(dagster_type[0])

        if not inner_type:
            raise DagsterInvalidDefinitionError(
                'Invalid member of array specification: {value} in list {the_list}'.format(
                    value=repr(dagster_type[0]), the_list=dagster_type
                )
            )
        return Array(inner_type)

    from dagster.core.types.dagster_type import DagsterType, List, ListType
    from dagster.core.types.python_set import Set, _TypedPythonSet
    from dagster.core.types.python_tuple import Tuple, _TypedPythonTuple

    if _is_config_type_class(dagster_type):
        check.param_invariant(
            False,
            'dagster_type',
            'Cannot pass a config type class to resolve_to_config_type. Got {dagster_type}'.format(
                dagster_type=dagster_type
            ),
        )

    if isinstance(dagster_type, type) and issubclass(dagster_type, DagsterType):
        raise DagsterInvalidDefinitionError(
            'You have passed a DagsterType class {dagster_type} to the config system. '
            'The DagsterType and config schema systems are seperate. '
            'Valid config values are:\n{desc}'.format(
                dagster_type=repr(dagster_type), desc=VALID_CONFIG_DESC,
            )
        )

    if is_typing_type(dagster_type):
        raise DagsterInvalidDefinitionError(
            (
                'You have passed in {dagster_type} to the config system. Types from '
                'the typing module in python are not allowed in the config system. '
                'You must use types that are imported from dagster or primitive types '
                'such as bool, int, etc.'
            ).format(dagster_type=dagster_type)
        )

    if dagster_type is List or isinstance(dagster_type, ListType):
        raise DagsterInvalidDefinitionError(
            'Cannot use List in the context of config. ' + helpful_list_error_string()
        )

    if dagster_type is Set or isinstance(dagster_type, _TypedPythonSet):
        raise DagsterInvalidDefinitionError(
            'Cannot use Set in the context of a config field. ' + helpful_list_error_string()
        )

    if dagster_type is Tuple or isinstance(dagster_type, _TypedPythonTuple):
        raise DagsterInvalidDefinitionError(
            'Cannot use Tuple in the context of a config field. ' + helpful_list_error_string()
        )

    if isinstance(dagster_type, DagsterType):
        raise DagsterInvalidDefinitionError(
            (
                'You have passed an instance of DagsterType {type_name} to the config '
                'system (Repr of type: {dagster_type}). '
                'The DagsterType and config schema systems are seperate. '
                'Valid config values are:\n{desc}'
            ).format(
                type_name=dagster_type.name if dagster_type.name else dagster_type.key,
                dagster_type=repr(dagster_type),
                desc=VALID_CONFIG_DESC,
            ),
        )

    # If we are passed here either:
    #  1) We have been passed a python builtin
    #  2) We have been a dagster wrapping type that needs to be convert its config varient
    #     e.g. dagster.List
    #  2) We have been passed an invalid thing. We return False to signify this. It is
    #     up to callers to report a reasonable error.

    from dagster.primitive_mapping import (
        remap_python_builtin_for_config,
        is_supported_config_python_builtin,
    )

    if is_supported_config_python_builtin(dagster_type):
        return remap_python_builtin_for_config(dagster_type)

    if dagster_type is None:
        return ConfigAnyInstance
    if BuiltinEnum.contains(dagster_type):
        return ConfigType.from_builtin_enum(dagster_type)

    # This means that this is an error and we are return False to a callsite
    # We do the error reporting there because those callsites have more context
    return False


class Field(object):
    '''Defines the schema for a configuration field.

    Fields are used in config schema instead of bare types when one wants to add a description,
    a default value, or to mark it as not required.

    Config fields are parsed according to their schemas in order to yield values available at
    pipeline execution time through the config system. Config fields can be set on solids, on custom
    data types (as the :py:func:`@input_hydration_schema <dagster.input_hydration_schema>`), and on
    other pluggable components of the system, such as resources, loggers, and executors.


    Args:
        config (Any): The schema for the config. This value can be any of:

            1. A Python primitive type that resolves to a Dagster config type 
               (:py:class:`~python:int`, :py:class:`~python:float`, :py:class:`~python:bool`,
               :py:class:`~python:str`, or :py:class:`~python:list`).

            2. A Dagster config type: :py:data:`~dagster.Int`, :py:data:`~dagster.Float`,
               :py:data:`~dagster.Bool`, :py:data:`~dagster.String`,
               :py:data:`~dagster.StringSource`, :py:data:`~dagster.Path`, :py:data:`~dagster.Any`,
               :py:class:`~dagster.Array`, :py:data:`~dagster.Noneable`, :py:data:`~dagster.Enum`,
               :py:class:`~dagster.Selector`, :py:class:`~dagster.Shape`, or
               :py:class:`~dagster.Permissive`.

            3. A bare python dictionary, which will be automatically wrapped in
               :py:class:`~dagster.Shape`. Values of the dictionary are resolved recursively
               according to the same rules.

            4. A bare python list of length one which itself is config type.
               Becomes :py:class:`Array` with list element as an argument.

        default_value (Any):
            A default value for this field, conformant to the schema set by the
            ``dagster_type`` argument. If a default value is provided, ``is_optional`` should be
            ``True``.

            Note: for config types that do post processing such as Enum, this value must be
            the pre processed version, ie use ``ExampleEnum.VALUE.name`` instead of ``ExampleEnum.VALUE``
        is_required (bool):
            Whether the presence of this field is required. Defaults to true. If ``is_required``
            is ``True``, no default value should be provided.
        is_optional (bool) (deprecated):
            Whether the presence of this field is optional. If ``is_optional`` is ``False``, no
            default value should be provided. Deprecated. Use ``is_required`` instead.
        description (str):
            A human-readable description of this config field.

    Examples:
        .. code-block::python

            @solid(
                config={
                    'word': Field(str, description='I am a word.'),
                    'repeats': Field(Int, default_value=1, is_required=False),
                }
            )
            def repeat_word(context):
                return context.solid_config['word'] * context.solid_config['repeats']

    '''

    def _resolve_config_arg(self, config):
        if isinstance(config, ConfigType):
            return config

        config_type = resolve_to_config_type(config)
        if not config_type:
            raise DagsterInvalidDefinitionError(
                (
                    'Attempted to pass {value_repr} to a Field that expects a valid '
                    'dagster type usable in config (e.g. Dict, Int, String et al).'
                ).format(value_repr=repr(config))
            )
        return config_type

    def __init__(
        self,
        config,
        default_value=FIELD_NO_DEFAULT_PROVIDED,
        is_optional=None,
        is_required=None,
        description=None,
    ):
        from .validate import validate_config
        from .post_process import post_process_config

        self.config_type = check.inst(self._resolve_config_arg(config), ConfigType)

        self.description = check.opt_str_param(description, 'description')

        check.opt_bool_param(is_optional, 'is_optional')
        check.opt_bool_param(is_required, 'is_required')

        if default_value != FIELD_NO_DEFAULT_PROVIDED:
            check.param_invariant(
                not (callable(default_value)), 'default_value', 'default_value cannot be a callable'
            )

        canonical_is_required = canonicalize_backcompat_args(
            new_val=is_required,
            new_arg='is_required',
            old_val=is_optional,
            old_arg='is_optional',
            coerce_old_to_new=lambda val: not val,
            additional_warn_txt='"is_optional" deprecated in 0.7.0 and will be removed in 0.8.0. Users should use "is_required" instead.',
        )

        if canonical_is_required is True:
            check.param_invariant(
                default_value == FIELD_NO_DEFAULT_PROVIDED,
                'default_value',
                'required arguments should not specify default values',
            )
        self._default_value = default_value

        # check explicit default value
        if self.default_provided:
            # invoke through property in case it is callable
            value = self.default_value
            evr = validate_config(self.config_type, value)
            if not evr.success:
                raise DagsterInvalidConfigError(
                    'Invalid default_value for Field.', evr.errors, default_value,
                )

        if canonical_is_required is None:
            # neither is_required nor is_optional were specified
            canonical_is_required = not all_optional_type(self.config_type)

            # on implicitly optional - set the default value
            # by resolving the defaults of the type
            if not canonical_is_required and self._default_value == FIELD_NO_DEFAULT_PROVIDED:
                evr = post_process_config(self.config_type, None)
                if not evr.success:
                    raise DagsterInvalidConfigError(
                        'Unable to resolve implicit default_value for Field.', evr.errors, None,
                    )
                self._default_value = evr.value
        self._is_required = canonical_is_required

    @property
    def is_required(self):
        return self._is_required

    @property
    def default_provided(self):
        '''Was a default value provided

        Returns:
            bool: Yes or no
        '''
        return self._default_value != FIELD_NO_DEFAULT_PROVIDED

    @property
    def default_value(self):
        check.invariant(self.default_provided, 'Asking for default value when none was provided')
        return self._default_value

    @property
    def default_value_as_str(self):
        check.invariant(self.default_provided, 'Asking for default value when none was provided')
        return str(self._default_value)

    def __repr__(self):
        return ('Field({config_type}, default={default}, is_required={is_required})').format(
            config_type=self.config_type,
            default='@'
            if self._default_value == FIELD_NO_DEFAULT_PROVIDED
            else self._default_value,
            is_required=self.is_required,
        )


def check_field_param(obj, param_name):
    return check.inst_param(obj, param_name, Field)


def check_opt_field_param(obj, param_name):
    return check.opt_inst_param(obj, param_name, Field)
