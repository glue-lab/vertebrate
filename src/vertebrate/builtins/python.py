"""
Implementations of ABCs using pure Python.
"""

import sys
from typing import Any, Protocol, runtime_checkable

from vertebrate.compute import Environment


@runtime_checkable
class WithAttributes(Protocol):

    __dict__: dict[str, Any]


class PythonEnvironment(Environment):
    """
    Execute functions or methods defined on a Python object.
    """

    def __init__(self, obj: WithAttributes):
        self.obj = obj

    def __contains__(self, item: str) -> bool:
        return hasattr(self.obj, item)

    def execute(self, executable: str, args: tuple = (), kwargs: dict = {}) -> Any:
        return getattr(self.obj, executable)(*args, **kwargs)
