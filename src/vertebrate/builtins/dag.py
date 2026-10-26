"""
Base class for Plans that make use of Order DAGs.
"""

import collections as cl
from collections.abc import Iterator

import networkx as nx

from vertebrate.data import Address
from vertebrate.plan import Plan

type DAG = dict[Address, list[Address]]
type Edge = tuple[Address, Address]


class DAGPlan(Plan):
    def _populate_dag(self, dag: DAG, address: Address) -> None:
        order = self.orders[address]
        for req in order.requirements:
            dag[address].append(req)
            if req not in dag:
                self._populate_dag(dag, req)

    def dag(self, address: Address) -> DAG:
        dag = cl.defaultdict(list)
        self._populate_dag(dag, address)
        return dag

    def _dag_edges(self, dag: DAG) -> Iterator[Edge]:
        for to_, froms in dag.items():
            for from_ in froms:
                yield from_, to_

    def _plan(self, address: Address) -> Iterator[Address]:
        D = nx.DiGraph()
        D.add_edges_from(self._dag_edges(self.dag(address)))
        yield from nx.topological_sort(D)
