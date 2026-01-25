# vertebrate: open backbones for data architecture

**vertebrate** is a Python package that defines generic interfaces for components commonly
used in data pipelines. Starting with some abstractions for compute, storage, and data
flow, we hope to make it something like an extension of
[collections.abc](https://docs.python.org/3/library/collections.abc.html) for
data-oriented projects.

## Installation

```bash
pip install vertebrate
```

## Basic Usage

```python
# Implement a computing environment that uses resources from the OS

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


# The environment is a collection of executables that can be called from Python
local_machine = OSEnvironment()
print(local_machine["ls"]("-l", ".").decode("utf-8"))  # Return type is bytes
local_machine["bash"]("-c", "echo $item", item="hello")  # Environment variables as kwargs

# Is git installed on your local machine?
"git" in local_machine

# Verify that this can return false
"not_a_program" in local_machine
```

Check out the built-in environment implementation for HTCondor! Installation:

```bash
pip install vertebrate[htcondor]
```

Import with:

```python
from vertebrate.builtins.htcondor import HTCondorEnvironment
```
