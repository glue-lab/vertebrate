"""
Example usage of the Plan base class using the LuigiPlan built-in.
"""

from vertebrate.builtins.luigi import LuigiPlan
from vertebrate.builtins.orders import SimpleOrders
from vertebrate.builtins.python import PythonEnvironment
from vertebrate.examples import orders as examples


def main():
    print("++ NOTE: This example requires the 'luigi' extra dependency group")
    print("-> pip install vertebrate[luigi]")
    print()

    print("++ Initialize some simple orders")
    print("-> orders = SimpleOrders(examples.specs, PythonEnvironment(examples))")
    orders = SimpleOrders(examples.specs, PythonEnvironment(examples))
    print()

    print("++ Initialize a Luigi-based execution plan")
    print("-> plan = LuigiPlan(orders)")
    plan = LuigiPlan(orders)
    print()

    print("++ Fulfill the order named 'file2'")
    print('-> plan.make("file2")')
    print("NOTE: This creates the following files in your working directory:")
    print("      file1, copy, file2, file1.txt, file2.txt")
    plan.make("file2")
    print()


if __name__ == "__main__":
    main()
