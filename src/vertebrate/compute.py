"""
ABCs for computing environments and executables.
"""

from abc import ABC, abstractmethod
from typing import Any


class Environment(ABC):

    @abstractmethod
    def execute(self, executable: str, args: tuple[Any], kwargs: dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def __contains__(self, item: str) -> bool:
        pass

    def __getitem__(self, key: str) -> "Action":
        if key not in self:
            raise KeyError(f"Item '{key}' not in {str(self)}")
        return Action(environment=self, executable=key)


class Action(object):

    def __init__(self, environment: Environment, executable: str) -> None:
        self._env = environment
        self._exe = executable

    @property
    def environment(self) -> Environment:
        return self._env

    @property
    def executable(self) -> str:
        return self._exe

    def __call__(self, *args, **kwargs) -> Any:
        return self.environment.execute(self.executable, args, kwargs)
