from vertebrate.testing import (
    DictNamespace,
    DictTransfers,
    EnvironmentContract,
    NamespaceContract,
    RecordingEnvironment,
    TemporaryContract,
    TransfersContract,
)


class TestRecordingEnvironment(EnvironmentContract):
    def make_environment(self):
        return RecordingEnvironment({"ls"})

    def present_executable(self):
        return "ls"

    def absent_executable(self):
        return "not_a_program"


class TestDictNamespace(NamespaceContract, TemporaryContract):
    def make_namespace(self):
        return DictNamespace({"a": 1})

    def present_address(self):
        return "a"

    def absent_address(self):
        return "missing"

    def populate(self, location):
        location.set(1)

    def test_temp_skips_addresses_already_in_use(self):
        namespace = DictNamespace({"tmp_0": "user data"})
        assert namespace.temp().address != "tmp_0"


class TestDictTransfers(TransfersContract):
    def make_transfers(self):
        return DictTransfers({(int, str): lambda source, target: None})

    def supported_datatypes(self):
        return (int, str)

    def unsupported_datatypes(self):
        return (str, int)
