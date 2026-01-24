"""
Implementations of ABCs that use the operating system directly
(ex. processes, files, sockets, etc.).
"""

import shutil
import subprocess
from typing import Any

from vertebrate.compute import Environment


class OSEnvironment(Environment):
    """
    Execute processes on the local operating system.
    """

    def _exe_path(self, item: str) -> str:
        return shutil.which(item)

    def __contains__(self, item: str) -> bool:
        return self._exe_path(item) is not None

    def execute(self, executable: str, args: tuple = (), kwargs: dict = {}) -> Any:
        exe_path = self._exe_path(executable)
        completed = subprocess.run((exe_path,) + args, env=kwargs, capture_output=True)
        return completed.stdout
