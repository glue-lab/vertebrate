"""
ABCs for computing environments and executables.
"""

from abc import ABC, abstractmethod
from typing import Any


# Should Environments be proper Namespaces? Some Locations can be executable
class Environment(ABC):

    @abstractmethod
    def execute(self, executable: str, args: tuple[Any], kwargs: dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def __contains__(self, item: str) -> bool:
        pass

    def __getitem__(self, key: str) -> "Action":
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


class Command(object):

    def __init__(
        self,
        action: Action,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] = {}
    ) -> None:
        self._action = action
        self._args = args
        self._kwargs = kwargs

    @property
    def action(self) -> Action:
        return self._action

    @property
    def args(self) -> tuple[Any, ...]:
        return self._args

    @property
    def kwargs(self) -> dict[str, Any]:
        return self._kwargs

    def __call__(self) -> Any:
        return self.action(*self.args, **self.kwargs)
