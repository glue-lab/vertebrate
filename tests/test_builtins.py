import pytest

import vertebrate.examples.orders as examples
from vertebrate.builtins.files import FileSystem
from vertebrate.builtins.orders import SimpleOrders
from vertebrate.builtins.python import PythonEnvironment
from vertebrate.builtins.variables import Dictionary
from vertebrate.testing import NamespaceContract, OrdersContract, TemporaryContract


class TestDictionary(NamespaceContract, TemporaryContract):
    def make_namespace(self):
        return Dictionary({"a": 1})

    def present_address(self):
        return "a"

    def absent_address(self):
        return "missing"

    def populate(self, location):
        location.set(1)


class TestFileSystem(NamespaceContract):
    @pytest.fixture(autouse=True)
    def present_file(self, tmp_path):
        (tmp_path / "present.json").write_text("{}")
        self.directory = tmp_path

    def make_namespace(self):
        return FileSystem()

    def present_address(self):
        return str(self.directory / "present.json")

    def absent_address(self):
        return str(self.directory / "absent.csv")


class TestSimpleOrders(OrdersContract):
    def make_namespace(self):
        return SimpleOrders(examples.specs, PythonEnvironment(examples))

    def present_address(self):
        return "file2"

    def absent_address(self):
        return "missing"

    def environment_name(self):
        return "PythonEnvironment"
