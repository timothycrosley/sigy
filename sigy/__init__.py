"""**sigy**

A library to enable reusing and composing Python function signatures.
"""
__version__ = "0.0.1"

from sigy import introspect
from sigy.inject import inject

__all__ = ["inject", "introspect", "__version__"]
