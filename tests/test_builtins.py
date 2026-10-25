from vertebrate.builtins.variables import Dictionary
from vertebrate.testing import NamespaceContract, TemporaryContract


class TestDictionary(NamespaceContract, TemporaryContract):
    def make_namespace(self):
        return Dictionary({"a": 1})

    def present_address(self):
        return "a"

    def absent_address(self):
        return "missing"

    def populate(self, location):
        location.set(1)
