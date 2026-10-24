"""
Tools for testing implementations of Vertebrate's ABCs.

- `vertebrate.testing.doubles`: minimal implementations that stand in for real
  environments, namespaces, transfer catalogs and orders in tests.

Nothing here depends on a test framework.
"""

from vertebrate.testing.doubles import (
    DictNamespace,
    DictTransfers,
    RecordingEnvironment,
    SpecOrder,
    SpecOrders,
    TemporaryValue,
    Value,
)

__all__ = [
    "DictNamespace",
    "DictTransfers",
    "RecordingEnvironment",
    "SpecOrder",
    "SpecOrders",
    "TemporaryValue",
    "Value",
]
