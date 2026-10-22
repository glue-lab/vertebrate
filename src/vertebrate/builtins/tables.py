"""
An implementation of a table namespace.
"""

import builtins

from sqlalchemy import MetaData, create_engine, exc
from sqlalchemy import Table as SQLTable

from vertebrate.data import Address, Location, Namespace


class Table(Location):
    def __call__(self):
        return SQLTable(
            self.address,
            self.namespace.meta,
            autoload_with=self.namespace.engine,
        )


class Database(Namespace):
    def __init__(self, db_url: str, *args, **kwargs) -> None:
        self.engine = create_engine(db_url, *args, **kwargs)
        self.meta = MetaData()

    def type(self, address: Address) -> builtins.type:
        # Rudimentary table typing
        return SQLTable

    @property
    def LocationType(self) -> builtins.type[Location]:
        return Table

    def __contains__(self, address: Address) -> bool:
        try:
            table = self[address]()
            return True
        except exc.NoSuchTableError:
            return False

    def __delitem__(self, address: Address) -> None:
        self[address]().drop(self.engine)
