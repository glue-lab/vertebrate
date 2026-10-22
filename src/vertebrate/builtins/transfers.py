"""
Implement a catalog of transfers.
"""

import networkx as nx
from pandas import DataFrame
from sqlalchemy import Table

from vertebrate.builtins.files import File, CSV, JSON, PARQUET
from vertebrate.builtins.variables import Dictionary, Value
from vertebrate.data import (
    Namespace,
    Location,
    LocationTypes,
    TemporaryLocation,
    Transfers,
    TransferImplementation,
)


### Transfer implementations


def dict_to_json_file(source: Value, target: File) -> None:
    import json

    with target.open("w") as file_out:
        json.dump(source.get(), file_out)


def json_file_to_dict(source: File, target: Value) -> None:
    import json

    with source.open("r") as file_in:
        target.set(json.load(file_in))


def table_to_df(source: Table, target: Value) -> None:
    from pandas import read_sql

    target.set(read_sql(source.address, source.namespace.engine))


def df_to_table(source: Value, target: Table) -> None:
    source.get().to_sql(
        target.address,
        target.namespace.engine,
        index=False,
    )


def parquet_to_df(source: File, target: Value) -> None:
    from pandas import read_parquet

    target.set(read_parquet(source.address))


def df_to_parquet(source: Value, target: File) -> None:
    source.get().to_parquet(
        target.address,
        engine="pyarrow",
        index=False,
    )


### Transfer catalog


class ExplicitTransfers(Transfers):
    catalog = {
        (dict, JSON): dict_to_json_file,
        (JSON, dict): json_file_to_dict,
        (Table, DataFrame): table_to_df,
        (DataFrame, Table): df_to_table,
        (PARQUET, DataFrame): parquet_to_df,
        (DataFrame, PARQUET): df_to_parquet,
    }

    def __getitem__(self, datatypes: LocationTypes) -> TransferImplementation | None:
        return self.catalog.get(datatypes)

    def __contains__(self, datatypes: LocationTypes) -> bool:
        return datatypes in self.catalog


def transfer_graph(edge_list):
    DG = nx.DiGraph()
    DG.add_edges_from(edge_list)
    return DG


HOW = "how"
variables = Dictionary(globals())


class PathTransfers(Transfers):
    catalog = transfer_graph(
        [
            (from_, to_, {HOW: how})
            for ((from_, to_), how) in ExplicitTransfers.catalog.items()
        ]
    )

    # Register namespaces used for generating temporary locations
    namespaces = {
        dict: variables,
        DataFrame: variables,
    }

    def _path(self, datatypes: LocationTypes) -> list[type]:
        source_type, target_type = datatypes
        try:
            return nx.shortest_path(
                self.catalog, source=source_type, target=target_type
            )
        except nx.exception.NetworkXNoPath:
            pass

    def _temp_loc(self, loc_type: type) -> TemporaryLocation:
        return self.namespaces[loc_type].temp()

    def _exec(self, step: LocationTypes, src_loc: Location, tgt_loc: Location) -> None:
        execute_this_step = self.catalog.edges[*step][HOW]
        execute_this_step(src_loc, tgt_loc)
        if isinstance(src_loc, TemporaryLocation):
            del src_loc.namespace[src_loc.address]

    def _exec_intermediate(self, step: LocationTypes, src_loc: Location) -> Location:
        _, target_type = step
        tgt_loc = self._temp_loc(target_type)
        self._exec(step, src_loc, tgt_loc)
        return tgt_loc

    def __getitem__(self, datatypes: LocationTypes) -> TransferImplementation | None:
        path = self._path(datatypes)
        if path is not None:

            def transfer(source: Location, target: Location) -> None:
                *steps, last = nx.utils.pairwise(path)
                src_loc = source
                for step in steps:
                    src_loc = self._exec_intermediate(step, src_loc)
                self._exec(last, src_loc, target)

            return transfer

    def __contains__(self, datatypes: LocationTypes) -> bool:
        return self._path(datatypes) is not None
