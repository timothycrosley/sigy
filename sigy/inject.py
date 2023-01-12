from __future__ import annotations

import itertools
from collections import defaultdict
from functools import wraps
from inspect import Parameter, _ParameterKind, signature
from typing import Any, Callable

from sigy import introspect

PARAM_GROUP_ORDER = ()


class NoOverridePressent:
    pass


def _generate_accepted_kwargs(function, kwargs) -> dict[str, Any]:
    """Dynamically creates a function that when called with dictionary of arguments will produce a kwarg that's
    compatible with the supplied function
    """
    if hasattr(function, "__code__") and introspect.takes_kwargs(function):
        function_takes_kwargs = True
        function_takes_arguments = []
    else:
        function_takes_kwargs = False
        function_takes_arguments = introspect.takes_arguments(function, *kwargs.keys())

    if function_takes_kwargs:
        return kwargs
    elif function_takes_arguments:
        return {key: value for key, value in kwargs.items() if key in function_takes_arguments}
    return {}


def inject(prefix_: str | None = None, shadow_: bool = False, **override_callbacks: Callable):
    """Injects a the provided callback functions as new parameters onto the wrapped function based on param_name=callback_function
    The wrapped function is then modified to take on the parameters of the given callback function and place the results as the
    parameter it replaced.

    Special modifying arguents
      - prefix_ - All arguments inherited by a given callback will have their name prefixed with this string.
      - shadow_ - If `True` the param being injected into will be hidden from the signature of the wrapped function.
    """

    def wrapper(function):
        function_signature = signature(function)
        type_overrides: dict[str, Any] = {}
        used_params: set[str] = set()
        kwdefaults: dict[str, Any] = (
            function.__kwdefaults__.copy() if function.__kwdefaults__ else {}
        )
        params: dict[str, Any] = {
            name: value for name, value in function_signature.parameters.items()
        }
        add_params: list[Parameter] = []

        for name, callback in override_callbacks.items():
            callback_signature = signature(callback)
            for param_name, param in callback_signature.parameters.items():
                type_override = callback.__annotations__.get(param_name)
                original_param_name = param_name
                if prefix_:
                    param_name = f"{prefix_}{param_name}"
                    param = Parameter(
                        name=param_name,
                        kind=param.kind,
                        default=param.default,
                        annotation=param.annotation,
                    )
                existing_type = type_overrides.get(name, function.__annotations__.get(param_name))
                existing_param = function_signature.parameters.get(param_name, None)
                if type_override:
                    if existing_type:
                        if type_override != existing_type:
                            raise TypeError(
                                f"Type mismatch introduced by sigy injected function {callback} "
                                f"parameter {param_name} requiring type {type_override} existing: {existing_type}."
                            )
                    elif existing_param:
                        if param != existing_param:
                            raise TypeError(
                                f"Param mismatch introduced by sigy injected function {callback} "
                                f"parameter {param_name} conflicts with existing: {existing_param}."
                            )
                    else:
                        type_overrides[param_name] = type_override
                        add_params.append(param)
                        params[param_name] = param
                if callback.__kwdefaults__ and original_param_name in callback.__kwdefaults__:
                    default_override = callback.__kwdefaults__[original_param_name]
                    if original_param_name in kwdefaults:
                        existing_default = kwdefaults[param_name]
                        if default_override != existing_default:
                            raise ValueError(
                                f"{callback} introduced incompatible default for {param_name} of {default_override} was {existing_default}"
                            )
                    else:
                        kwdefaults[param_name] = default_override

        @wraps(function)
        def wrapped_function(*args, **kwargs):
            if prefix_:
                callback_kwargs = {
                    key.split(prefix_, 1)[1]: value
                    for key, value in kwargs.items()
                    if key.startswith(prefix_)
                }
            else:
                callback_kwargs = kwargs
            for name, callback in override_callbacks.items():
                accepted_params = _generate_accepted_kwargs(callback, callback_kwargs)
                if prefix_:
                    used_params.update((f"{prefix_}{key}" for key in accepted_params.keys()))
                else:
                    used_params.update(accepted_params.keys())
                if name not in kwargs:
                    kwargs[name] = callback(*args, **accepted_params)

            function_params = _generate_accepted_kwargs(function, kwargs)
            used_params.update(function_params.keys())
            unused_params = set(kwargs.keys()).difference(used_params)
            if unused_params:
                raise TypeError(
                    f"{function.__name__}() got unexpected keyword argument(s): {', '.join(unused_params)}"
                )
            return function(*args, **function_params)

        wrapped_function.__annotations__.update(type_overrides)

        grouped_params: dict[_ParameterKind, list[Parameter]] = defaultdict(list)
        if shadow_:
            existing_params = (
                value
                for key, value in function_signature.parameters.items()
                if key not in override_callbacks
            )
            for key in override_callbacks:
                wrapped_function.__annotations__.pop(key)
        else:
            existing_params = function_signature.parameters.values()
        for group, params in itertools.groupby(
            itertools.chain(existing_params, add_params),
            key=lambda param: param.kind,
        ):
            grouped_params[group].extend(params)

        wrapped_function_signature = function_signature.replace(
            parameters=itertools.chain(*(grouped_params[key] for key in sorted(grouped_params)))
        )
        wrapped_function.__signature__ = wrapped_function_signature
        if kwdefaults:
            wrapped_function.__kwdefaults__ = kwdefaults
        return wrapped_function

    return wrapper
