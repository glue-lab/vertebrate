"""
Example usage of the Environment base class using the OSEnvironment built-in.
"""

from vertebrate.builtins.os import OSEnvironment


def main():
    print("++ Get a reference to the OS environment -> local_machine = OSEnvironment()")
    local_machine = OSEnvironment()
    print()

    print('++ Reference the ls executable -> ls = local_machine["ls"]')
    ls = local_machine["ls"]
    print()

    print('++ Execute `ls -l .` -> ls("-l", ".")')
    print(local_machine["ls"]("-l", ".").decode("utf-8"))
    # ^^ Return type is bytes
    print()

    msg = "++ Environment variables can be passed in as kwargs"
    msg += '\n-> sh("-c", "printf $item", item="hello")'
    print(msg)
    print(local_machine["sh"]("-c", "printf $item", item="hello").decode("utf-8"))
    print()

    print('++ Is cd installed on your local machine? -> "cd" in local_machine')
    print("cd" in local_machine)
    print()

    print('++ Verify that this can return false -> "not_a_program" in local_machine')
    print("not_a_program" in local_machine)
    print()


if __name__ == "__main__":
    main()
