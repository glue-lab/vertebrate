"""
Implementations of ABCs that use remote OS resources via SSH.
"""

import shlex
import subprocess
from typing import Any

from vertebrate.compute import Environment


class SSHEnvironment(Environment):
    """
    Execute processes on a remote OS via SSH.
    """

    # These implementations are often a matter of expression;
    # SSH could be called directly using an OSEnvironment instance.

    def __init__(
        self,
        user: str,
        host: str,
        options: tuple[str, ...] = (),
        check: bool = True,
    ) -> None:
        self.user = user
        self.host = host
        self.options = options
        self.check = check

    def _exec_ssh(
        self,
        executable: str,
        args: tuple = (),
        kwargs: dict = {},
        check: bool = True,
    ) -> Any:
        # ssh hands the remote shell one string, so quote each argument into it
        assignments = [f"{key}={value}" for key, value in kwargs.items()]
        argv = ["env", *assignments] if assignments else []
        command = shlex.join([*argv, executable, *args])
        try:
            completed = subprocess.run(
                ("ssh", *self.options, f"{self.user}@{self.host}", command),
                capture_output=True,
                check=check,
            )
        except subprocess.CalledProcessError as error:
            if error.stderr:
                error.add_note(error.stderr.decode("utf-8", errors="replace"))
            raise
        return completed.stdout

    def __contains__(self, item: str) -> bool:
        try:
            self._exec_ssh("which", args=(item,))
        except subprocess.CalledProcessError as error:
            if error.returncode == 1:  # `which` found nothing
                return False
            raise
        return True

    def execute(self, executable: str, args: tuple = (), kwargs: dict = {}) -> Any:
        return self._exec_ssh(executable, args=args, kwargs=kwargs, check=self.check)
