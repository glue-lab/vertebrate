"""
Tools for testing implementations of Vertebrate's ABCs.

- `vertebrate.testing.contracts`: implementation-agnostic test suites that an
  implementation inherits by subclassing.
- `vertebrate.testing.doubles`: minimal implementations that stand in for real
  environments, namespaces, transfer catalogs and orders in tests.

Nothing here depends on a test framework.
"""

from vertebrate.testing.contracts import (
    EnvironmentContract,
    NamespaceContract,
    OrdersContract,
    PlanContract,
    TemporaryContract,
    TransfersContract,
)
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
    "EnvironmentContract",
    "NamespaceContract",
    "OrdersContract",
    "PlanContract",
    "RecordingEnvironment",
    "SpecOrder",
    "SpecOrders",
    "TemporaryContract",
    "TemporaryValue",
    "TransfersContract",
    "Value",
]
