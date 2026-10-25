from vertebrate.testing import EnvironmentContract, RecordingEnvironment


class TestRecordingEnvironment(EnvironmentContract):
    def make_environment(self):
        return RecordingEnvironment({"ls"})

    def present_executable(self):
        return "ls"

    def absent_executable(self):
        return "not_a_program"
