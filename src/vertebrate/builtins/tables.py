"""
An implementation of a table namespace.
"""

from contextlib import closing
from typing import Type

from sqlalchemy import create_engine, exc, MetaData, Table as SQLTable
from sqlalchemy.orm import Session

from data import Namespace, Location, Address


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

    def type(self, address: Address) -> type:
        # Rudimentary table typing
        return SQLTable

    @property
    def LocationType(self) -> Type[Location]:
        return Table

    def __contains__(self, address: Address) -> bool:
        try:
            table = self[address]()
            return True
        except exc.NoSuchTableError:
            return False

    def __delitem__(self, address: Address) -> None:
        self[address]().drop(self.engine)
