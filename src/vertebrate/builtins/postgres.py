"""
Implementation of a PostgreSQL database as an execution environment.
"""

from typing import Any

from sqlalchemy import create_engine, Engine, MetaData, Table
from sqlalchemy.sql import and_, func, functions, quoted_name, select

from vertebrate.compute import Environment


class PostgresEnvironment(Environment):
    """
    Call stored procedures defined in a PostgreSQL database.
    """

    @staticmethod
    def _postgres_engine(user: str, dbname: str, host: str, port: str) -> Engine:
        url = f"postgresql+psycopg2://{user}@{host}:{port}/{dbname}"
        return create_engine(url, echo=False)

    def __init__(self, user: str, dbname: str, host: str, port: str) -> None:
        self.engine = PostgresEnvironment._postgres_engine(user, dbname, host, port)
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
        if not id_name:
            return id_name
        if id_name.startswith('"'):
            return id_name.strip('"')
        else:
            return id_name.lower()

    @staticmethod
    def _parse_exec_name(exec_name: str) -> dict[str, str]:

        # Extract schema name from executable name if present
        schema_name = None
        if "." in exec_name:
            schema_name, exec_name = exec_name.split(".")

        return {
            "schema": PostgresEnvironment._identifier_name(schema_name),
            "name": PostgresEnvironment._identifier_name(exec_name),
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
        info = PostgresEnvironment._parse_exec_name(item)
        with self:
            if info["schema"] is None:
                return self._contains_unqualified(info["name"])
            else:
                return self._contains_qualified(info["schema"], info["name"])

    @staticmethod
    def _sql_call(executable: str) -> functions._FunctionGenerator:
        info = PostgresEnvironment._parse_exec_name(executable)
        if info["schema"] is None:
            sql_call = getattr(func, quoted_name(info["name"], quote=True))
        else:
            sql_schema = getattr(func, quoted_name(info["schema"], quote=True))
            sql_call = getattr(sql_schema, quoted_name(info["name"], quote=True))
        return sql_call        

    def execute(self, executable: str, args: tuple = (), kwargs: dict = {}) -> Any:
        with self:
            result = self.conn.execute(
                select(PostgresEnvironment._sql_call(executable)(*args))
            )
            return result
