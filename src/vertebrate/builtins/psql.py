"""
Implementation of a PSQL execution environment.
"""

import os
import shutil
import subprocess
from typing import Any

from vertebrate.compute import Environment


class PSQLEnvironment(Environment):
    """
    Execute psql invocations with connection info passed as arguments.
    """

    def __init__(self, user: str, dbname: str, host: str, port: str):
        self.user = user
        self.dbname = dbname
        self.host = host
        self.port = port
        self.psql = self._find_psql_on_path()

    def _find_psql_on_path(self) -> str:
        psql_path = shutil.which("psql")
        if psql_path is None:
            raise ValueError("psql not found on PATH")
        return psql_path

    def _connection_args(self):
        return (
            "-U", self.user,
            "-d", self.dbname,
            "-h", self.host,
            "-p", self.port,
        )

    def execute(
        self,
        executable: str,
        args: tuple = (),
        kwargs: dict = {},
    ) -> Any:
        if executable not in self:
            raise KeyError(f"Executable not found: {executable}")
        completed = subprocess.run(
            (self.psql,) + self._connection_args() + ("-f", executable),
            env={**os.environ, **kwargs},
            capture_output=True,
        )
        return completed.stdout.decode("utf-8")

    def __contains__(self, item: str) -> bool:
        return os.path.exists(item)
