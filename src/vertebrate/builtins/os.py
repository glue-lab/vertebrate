"""
Implementations of ABCs that use the operating system directly
(ex. processes, files, sockets, etc.).
"""

import os
import shutil
import subprocess
from typing import Any

from vertebrate.compute import Environment


class OSEnvironment(Environment):
    """
    Execute processes on the local operating system.
    """

    def __init__(self, check: bool = True) -> None:
        self.check = check

    def _exe_path(self, item: str) -> str | None:
        return shutil.which(item)

    def __contains__(self, item: str) -> bool:
        return self._exe_path(item) is not None

    def execute(self, executable: str, args: tuple = (), kwargs: dict = {}) -> Any:
        exe_path = self._exe_path(executable)
        if exe_path is None:
            raise KeyError(f"Executable not found: {executable}")
        try:
            completed = subprocess.run(
                (exe_path,) + args,
                env={**os.environ, **kwargs},
                capture_output=True,
                check=self.check,
            )
        except subprocess.CalledProcessError as error:
            if error.stderr:
                error.add_note(error.stderr.decode("utf-8", errors="replace"))
            raise
        return completed.stdout
