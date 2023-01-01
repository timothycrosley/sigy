from functools import wraps
from inspect import Parameter, signature
from typing import Any, Callable

from sigy import introspect


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


def inject(**override_callbacks: Callable):
    def wrapper(function):
        function_signature = signature(function)
        type_overrides: dict[str, Any] = {}
        params: dict[str, Any] = {name: value for name, value in function_signature.parameters.items()}
        add_params: list[Parameter] = []
        
        for name, callback in override_callbacks.items():
            callback_signature = signature(callback)
            for param_name, param in callback_signature.parameters.items():
                type_override = callback.__annotations__.get(param_name)

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

        @wraps(function)
        def wrapped_function(*args, **kwargs):
            for name, callback in override_callbacks.items():
                if name not in kwargs:
                    kwargs[name] = callback(*args, **_generate_accepted_kwargs(callback, kwargs))
            return function(*args, **_generate_accepted_kwargs(function, kwargs))

        wrapped_function.__annotations__.update(type_overrides)

        wrapped_function_signature = function_signature.replace(
            parameters=[*function_signature.parameters.values(), *add_params]
        )
        wrapped_function.__signature__ = wrapped_function_signature
        return wrapped_function

    return wrapper
