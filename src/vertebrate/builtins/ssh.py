"""
Implementations of ABCs that use remote OS resources via SSH.
"""

import subprocess
from typing import Any

from vertebrate.compute import Environment


class SSHEnvironment(Environment):
    """
    Execute processes on a remote OS via SSH.
    """

    # These implementations are often a matter of expression;
    # SSH could be called directly using an OSEnvironment instance.

    def __init__(self, user: str, host: str) -> None:
        self.user = user
        self.host = host

    def _exec_ssh(self, executable: str, args: tuple = (), kwargs: dict = {}) -> Any:
        completed = subprocess.run(
            ("ssh", f"{self.user}@{self.host}", executable) + args,
            capture_output=True,
        )
        return completed.stdout    

    def __contains__(self, item: str) -> bool:
        exe_path = self._exec_ssh("which", args=(item,))
        return len(exe_path) > 0

    def execute(self, executable: str, args: tuple = (), kwargs: dict = {}) -> Any:
        return self._exec_ssh(executable, args=args, kwargs=kwargs)
