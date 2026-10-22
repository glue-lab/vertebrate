"""
An implementation of a file namespace.
"""

import builtins
from pathlib import Path
from typing import IO

from vertebrate.data import Address, Location, Namespace

# Datatypes that will be inferred by file extension
CSV = "csv"
JSON = "json"
JSONLINES = "jsonl"
YAML = "yaml"
PARQUET = "parquet"
XML = "xml"
HTML = "html"
TOML = "toml"


class CSV: ...


class JSON: ...


class JSONLINES: ...


class YAML: ...


class PARQUET: ...


class XML: ...


class HTML: ...


class TOML: ...


class File(Location):
    def open(self, *args, **kwargs) -> IO:
        return open(self.address, *args, **kwargs)


class FileSystem(Namespace):
    extensions = {
        ".csv": CSV,
        ".json": JSON,
        ".jsonl": JSONLINES,
        ".jl": JSONLINES,
        ".yaml": YAML,
        ".yml": YAML,
        ".parquet": PARQUET,
        ".xml": XML,
        ".html": HTML,
        ".htm": HTML,
        ".toml": TOML,
    }

    def type(self, address: Address) -> type:
        ext = Path(address).suffix
        if ext in self.extensions:
            return self.extensions[ext]
        else:
            return bytes

    @property
    def LocationType(self) -> builtins.type[Location]:
        return File

    def __contains__(self, address: Address) -> bool:
        return Path(address).exists()

    def __delitem__(self, address: Address) -> None:
        Path(address).unlink()
