"""
Implementation of a PostgreSQL database as an execution environment.
"""

import string
from typing import Any

from sqlalchemy import create_engine, Engine, MetaData, Table, TextClause, text
from sqlalchemy.sql import and_, func, select

from vertebrate.compute import Environment


ASCII_LOWERCASE = str.maketrans(string.ascii_uppercase, string.ascii_lowercase)


class PostgresEnvironment(Environment):
    """
    Call stored procedures defined in a PostgreSQL database.
    """

    @staticmethod
    def _postgres_engine(user: str, dbname: str, host: str, port: str) -> Engine:
        url = f"postgresql+psycopg2://{user}@{host}:{port}/{dbname}"
        return create_engine(url, echo=False)

    def __init__(self, user: str, dbname: str, host: str, port: str) -> None:
        self.engine = self._postgres_engine(user, dbname, host, port)
        self.meta = MetaData()
        self.conn = self.engine.connect()

    def __enter__(self):
        self.trans = self.conn.begin()
        return self

    def __exit__(self, type_, value, traceback):
        if type_:
            self.trans.rollback()
        else:
            self.trans.commit()

    @staticmethod
    def _identifier_name(id_name: str) -> str:
        # As PostgreSQL resolves one: quoted is literal, unquoted folds only A-Z
        if len(id_name) >= 2 and id_name[0] == id_name[-1] == '"':
            quoted = id_name[1:-1]
            if quoted and '"' not in quoted.replace('""', ""):
                return quoted.replace('""', '"')
        elif id_name and '"' not in id_name:
            return id_name.translate(ASCII_LOWERCASE)
        raise ValueError(f"Invalid identifier: {id_name!r}")

    @staticmethod
    def _split_qualified(exec_name: str) -> list[str]:
        parts, current, quoted = [], "", False
        for char in exec_name:
            if char == '"':
                quoted = not quoted
            if char == "." and not quoted:
                parts.append(current)
                current = ""
            else:
                current += char
        parts.append(current)
        return parts

    @classmethod
    def _parse_exec_name(cls, exec_name: str) -> dict[str, str | None]:
        parts = cls._split_qualified(exec_name)
        if len(parts) > 2:
            raise ValueError(f"Expected [schema.]name, got {exec_name!r}")
        *schema, name = parts
        return {
            "schema": cls._identifier_name(schema[0]) if schema else None,
            "name": cls._identifier_name(name),
        }

    def _pg_proc(self) -> Table:
        return Table(
            "pg_proc",
            self.meta,
            autoload_with=self.engine,
            schema="pg_catalog",
        )

    def _pg_namespace(self) -> Table:
        return Table(
            "pg_namespace",
            self.meta,
            autoload_with=self.engine,
            schema="pg_catalog",
        )

    def _contains_unqualified(self, exec_name: str) -> bool:
        p = self._pg_proc()
        n = self._pg_namespace()
        num_items = self.conn.execute(
            select(func.count()).\
            where(and_(
                p.c.proname == exec_name,
                p.c.pronamespace == n.c.oid,
                n.c.nspname == func.any(func.current_schemas(True)),
            ))
        ).scalar_one()
        return num_items > 0

    def _contains_qualified(self, schema_name: str, exec_name: str) -> bool:
        p = self._pg_proc()
        n = self._pg_namespace()
        num_items = self.conn.execute(
            select(func.count()).\
            where(and_(
                p.c.proname == exec_name,
                p.c.pronamespace == n.c.oid,
                n.c.nspname == schema_name,
            ))
        ).scalar_one()
        return num_items > 0

    def __contains__(self, item: str) -> bool:
        info = self._parse_exec_name(item)
        with self:
            if info["schema"] is None:
                return self._contains_unqualified(info["name"])
            else:
                return self._contains_qualified(info["schema"], info["name"])

    @staticmethod
    def _quote_identifier(id_name: str) -> str:
        # Colons are escaped so text() doesn't read them as bind parameters
        return '"' + id_name.replace('"', '""').replace(":", "\\:") + '"'

    @classmethod
    def _sql_call(cls, executable: str, args: tuple) -> TextClause:
        info = cls._parse_exec_name(executable)
        parts = [info["schema"], info["name"]]
        qualified = ".".join(cls._quote_identifier(p) for p in parts if p is not None)
        params = {f"arg{i}": arg for i, arg in enumerate(args)}
        placeholders = ", ".join(f":{key}" for key in params)
        return text(f"SELECT {qualified}({placeholders})").bindparams(**params)

    def execute(self, executable: str, args: tuple = (), kwargs: dict = {}) -> Any:
        with self:
            result = self.conn.execute(self._sql_call(executable, args))
            return result
