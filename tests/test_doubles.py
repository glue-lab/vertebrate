from vertebrate.testing import (
    DictNamespace,
    DictTransfers,
    EnvironmentContract,
    NamespaceContract,
    OrdersContract,
    RecordingEnvironment,
    SpecOrders,
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


class TestSpecOrders(OrdersContract):
    def make_namespace(self):
        spec = {
            "build": {"env": "shell", "exe": "make", "requirements": ["fetch"]},
            "fetch": {"env": "shell", "exe": "curl"},
        }
        return SpecOrders(spec, {"shell": RecordingEnvironment({"make", "curl"})})

    def present_address(self):
        return "build"

    def absent_address(self):
        return "missing"

    def environment_name(self):
        return "shell"
