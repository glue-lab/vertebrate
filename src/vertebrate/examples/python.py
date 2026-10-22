"""
Example usage of the Environment base class using the PythonEnvironment built-in.
"""

import sys

from vertebrate.builtins.python import PythonEnvironment

type Numeric = int | float


def subtract(a: Numeric, b: Numeric) -> Numeric:
    return a - b


class AddTo(object):
    def __init__(self, x: Numeric):
        self.x = x

    def plus(self, y: Numeric):
        return self.x + y


def main():
    print("++ Get a reference to this module")
    print("-> this_module = PythonEnvironment(sys.modules[__name__])")
    this_module = PythonEnvironment(sys.modules[__name__])
    print()

    print("++ Is there a function named 'subtract' in this module?")
    print('-> "subtract" in this_module')
    print("subtract" in this_module)
    print()

    print('++ Execute it -> this_module["subtract"](5.0, 3)')
    print(this_module["subtract"](5.0, 3))
    print()

    print("++ Construct a PythonEnvironment from an object")
    print("-> five = PythonEnvironment(AddTo(5))")
    five = PythonEnvironment(AddTo(5))
    print()

    print('++ Execute one of its methods -> five["plus"](4)')
    print(five["plus"](4))
    print()


if __name__ == "__main__":
    main()
