"""
An example set of executables and order specs.
"""


def populate_file(path: str, content: str) -> None:
    with open(path, "w") as file_out:
        file_out.write(content)


def read_file(path: str) -> None:
    with open(path, "r") as file_in:
        print(file_in.read())


specs = {
    "file1": {
        "env": "PythonEnvironment",
        "exe": "populate_file",
        "args": ["file1.txt", "Hello, Vertebrate"],
        "requirements": [],
    },
    "copy": {
        "env": "OSEnvironment",
        "exe": "cp",
        "args": ["file1.txt", "file2.txt"],
        "requirements": ["file1"],
    },
    "file2": {
        "env": "PythonEnvironment",
        "exe": "read_file",
        "args": ["file2.txt"],
        "requirements": ["copy"],
    },
}
