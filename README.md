# vertebrate: open backbones for data architecture

**vertebrate** is a Python package that defines generic interfaces for components commonly
used in data pipelines. Starting with some abstractions for compute, storage, and data
flow, we hope to make it something like an extension of
[collections.abc](https://docs.python.org/3/library/collections.abc.html) for
data-oriented projects.

While the package contains built-in implementations for these interfaces, they are
included as references to demonstrate usage of the main classes and are not intended to be
definitive. You may find them useful, and you can use them if you wish, but we really
hope that Vertebrate's main contribution is the "backbones" outlining general patterns for
data processing that don't tightly couple with any given system or format. We encourage
you to flesh them out in a way that works for you.

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

**NOTE:** Many of the examples create small files in your working directory.
Examples are best run from a test folder.

----

Check out the built-in environment implementation for HTCondor! Installation:

```bash
pip install vertebrate[htcondor]
```

Import with:

```python
from vertebrate.builtins.htcondor import HTCondorEnvironment
```
