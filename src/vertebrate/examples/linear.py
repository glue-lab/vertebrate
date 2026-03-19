"""
Example usage of the Plan base class using the LinearPlan built-in.
"""

from vertebrate.builtins.linear import LinearPlan
from vertebrate.builtins.orders import SimpleOrders
from vertebrate.builtins.python import PythonEnvironment
from vertebrate.examples import orders as examples


def main():
    print("++ NOTE: This example requires the 'dag' extra dependency group")
    print("-> pip install vertebrate[dag]")
    print()

    print("++ Initialize some simple orders")
    print("-> orders = SimpleOrders(examples.specs, PythonEnvironment(examples))")
    orders = SimpleOrders(examples.specs, PythonEnvironment(examples))
    print()

    print("++ Initialize a linear execution plan")
    print("-> plan = LinearPlan(orders)")
    plan = LinearPlan(orders)
    print()

    print("++ Fulfill the order named 'file2'")
    print('-> plan.make("file2")')
    print("NOTE: This creates file1.txt and file2.txt in your working directory")
    plan.make("file2")
    print()


if __name__ == "__main__":
    main()
