from functools import wraps
from typing import Callable


def inject(**override_callbacks: Callable):
    def wrapper(function):
        @wraps(function)
        def wrapped_function(*args, **kwargs):
            for name, callback in override_callbacks.items():
                kwargs[name] = callback(*args, **kwargs)
            return function(*args, **kwargs)

        return wrapped_function

    return wrapper
