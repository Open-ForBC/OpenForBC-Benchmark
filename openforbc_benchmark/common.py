"""The common module contains shared classes."""

from __future__ import annotations
from typing import TYPE_CHECKING

from openforbc_benchmark.json import Serializable

if TYPE_CHECKING:
    from typing import Any, Optional


class Command(Serializable):
    """
    A benchmark command which can be executed.

    Contains the command arguments and optionally some environment data.
    """

    def __init__(
        self,
        command: str | list[str],
        env: dict[str, str] = {},
        workdir: Optional[str] = None,
    ) -> None:
        """Create a new command object."""
        from shlex import split

        if not isinstance(command, list):
            self.command = split(command)
        else:
            self.command = command

        self.env = env
        self.workdir = workdir

    @classmethod
    def deserialize(cls, json: Any) -> Command:
        if isinstance(json, str):
            return cls(json)
        elif isinstance(json, dict):
            return cls(**json)
        else:
            assert False

    @classmethod
    def deserialize_commands(cls, json: Any) -> list[Command]:
        commands = [json] if not isinstance(json, list) else json

        return [Command.deserialize(c) for c in commands]
