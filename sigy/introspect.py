"""Defines built in functions to aid in introspection"""
from __future__ import absolute_import


def is_coroutine(function):
    """Returns True if the passed in function is a coroutine"""
    return function.__code__.co_flags & 0x0080 or getattr(function, "_is_coroutine", False)


def arguments(function, extra_arguments=0):
    """Returns the name of all arguments a function takes"""
    if not hasattr(function, "__code__"):
        return ()

    return function.__code__.co_varnames[: function.__code__.co_argcount + extra_arguments]


def takes_kwargs(function):
    """Returns True if the supplied function takes keyword arguments"""
    return bool(function.__code__.co_flags & 0x08)


def takes_args(function):
    """Returns True if the supplied functions takes extra non-keyword arguments"""
    return bool(function.__code__.co_flags & 0x04)


def takes_arguments(function, *named_arguments):
    """Returns the arguments that a function takes from a list of requested arguments"""
    return set(named_arguments).intersection(arguments(function))


def takes_all_arguments(function, *named_arguments):
    """Returns True if all supplied arguments are found in the function"""
    return bool(takes_arguments(function, *named_arguments) == set(named_arguments))
