# Copyright (c) 2021-2022 Istituto Nazionale di Fisica Nucleare
# SPDX-License-Identifier: MIT

"""`state` module holds common state information across the CLI modules."""

from os import getcwd

state = {"search_path": getcwd()}
