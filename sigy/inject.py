from functools import wraps
from typing import Callable, Any
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
        @wraps(function)
        def wrapped_function(*args, **kwargs):
            for name, callback in override_callbacks.items():
                kwargs[name] = callback(*args, **_generate_accepted_kwargs(callback, kwargs))
            return function(*args, **_generate_accepted_kwargs(function, kwargs))

        return wrapped_function

    return wrapper
