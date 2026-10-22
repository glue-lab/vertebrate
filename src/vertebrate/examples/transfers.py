"""
Example showing data transfer between Locations among Namespaces.
"""

from pandas import DataFrame

from vertebrate.builtins.files import FileSystem
from vertebrate.builtins.tables import Database
from vertebrate.builtins.transfers import ExplicitTransfers, PathTransfers
from vertebrate.builtins.variables import Dictionary
from vertebrate.data import Transfer

if __name__ == "__main__":
    print("++ NOTE: This example requires the 'transfers' extra dependency group")
    print("-> pip install vertebrate[transfers]")
    print()

    print("++ Define a catalog of ways to transfer data")
    print("-> Transfer.catalog = ExplicitTransfers()")
    Transfer.catalog = ExplicitTransfers()
    print()

    print("++ Get a reference to this module's variable namespace")
    print("-> variables = Dictionary(globals())")
    variables = Dictionary(globals())
    print()

    print("++ Get a reference to your filesystem")
    print("-> files = FileSystem()")
    files = FileSystem()
    print()

    print("++ Define example data")
    print('-> data = {"a": "Athabasca", "b": "Bosphorus", "c": "Cerulean"}')
    data = {"a": "Athabasca", "b": "Bosphorus", "c": "Cerulean"}
    print()

    print("++ Write example data to file as JSON")
    print('-> (variables["data"] >> files["example.json"])()')
    print("NOTE: This creates example.json in your working directory")
    (variables["data"] >> files["example.json"])()
    print()

    print("++ Read data back into the variable 'restored'")
    print('-> (variables["restored"] << files["example.json"])(target=dict)')
    (variables["restored"] << files["example.json"])(target=dict)
    print()

    print("++ Contents of the 'restored' variable")
    print("-> print(restored)")
    print(restored)  # noqa: F821
    print()

    print("++ Define some example tabular data in a Pandas DataFrame")
    print(
        '-> example = DataFrame({"a": ["Athabasca"], "b": ["Bosphorus"], "c": ["Cerulean"]})'
    )
    example = DataFrame({"a": ["Athabasca"], "b": ["Bosphorus"], "c": ["Cerulean"]})
    print()

    print("++ Get a reference to a SQLite table namespace")
    print('-> tables = Database("sqlite:///example.db")')
    print("++ NOTE: This creates example.db in your working directory")
    tables = Database("sqlite:///example.db")
    print()

    print("++ Populate an example table with the DataFrame")
    print('-> (variables["example"] >> tables["example"])()')
    (variables["example"] >> tables["example"])()
    print()

    print("++ Switch catalog to one that computes multi-step transfers")
    print("-> Transfer.catalog = PathTransfers()")
    Transfer.catalog = PathTransfers()
    print()

    print("++ Transfer data from a SQLite table to a Parquet file")
    print("   (internally, uses a DataFrame as an intermediate)")
    print('-> (tables["example"] >> files["example.parquet"])()')
    print("NOTE: This creates example.parquet in your working directory")
    (tables["example"] >> files["example.parquet"])()
    print()

    print("++ (Take a look at the contents of the 'example' table in example.db")
    print("    and the file example.parquet)")
    print()
