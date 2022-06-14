"""`state` module holds common state information across the CLI modules."""

from os import getcwd

state = {"search_path": getcwd()}
