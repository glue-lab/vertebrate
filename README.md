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

Check out the examples in `vertebrate.examples`! For instance, this example shows how to
use the built-in OS environment:

```bash
python -m vertebrate.examples.os
```

Check out the built-in environment implementation for HTCondor! Installation:

```bash
pip install vertebrate[htcondor]
```

Import with:

```python
from vertebrate.builtins.htcondor import HTCondorEnvironment
```
