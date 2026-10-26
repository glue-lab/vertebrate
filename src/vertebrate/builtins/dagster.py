"""
Implementation of a Plan that uses the Dagster framework for orchestration.
"""

import dagster as dg

from vertebrate.builtins.dag import DAGPlan
from vertebrate.builtins.utils import format_address
from vertebrate.data import Address


class DagsterPlan(DAGPlan):
    def _construct_asset(self, order_name: Address) -> dg.AssetsDefinition:

        ins = {
            format_address(req): dg.AssetIn(key=format_address(req))
            for req in self.orders[order_name].requirements
        }

        @dg.asset(name=format_address(order_name), ins=ins)
        def _asset(**kwargs):
            self.orders[order_name]()

        return _asset

    def assets(self, address: Address) -> None:
        return [self._construct_asset(order_name) for order_name in self._plan(address)]

    def make(self, address: Address) -> None:
        dg.materialize(self.assets(address))
