import os
import sys

from pyhulk.parser import repl

def get_command(command: list = sys.argv[1]):
    """Macros to manage the db"""
    if command == "repl":
        repl()
    else:
        print(f"Bad command {command}")


if __name__ == "__main__":
    get_command()
