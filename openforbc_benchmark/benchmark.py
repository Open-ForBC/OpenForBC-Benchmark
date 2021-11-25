from __future__ import annotations
from typing import TYPE_CHECKING

from openforbc_benchmark.common import Command
from openforbc_benchmark.json import Serializable

if TYPE_CHECKING:
    from typing import Any


class Benchmark(Serializable):
    """A benchmark."""

    def __init__(
        self,
        name: str,
        description: str,
        setup_commands: list[Command] | None,
        run_commands: list[Command],
        cleanup_commands: list[Command] | None,
        stats: Command | dict[str, StatMatchInfo],
        virtualenv: bool,
    ) -> None:
        """Create a Benchmark object."""
        self.name = name
        self.description = description
        self.setup_commands = setup_commands
        self.run_commands = run_commands
        self.cleanup_commands = cleanup_commands
        self.stats = stats
        self.virtualenv = virtualenv

    @classmethod
    def deserialize(cls, json: Any) -> Benchmark:
        cls.validate(json)

        setup_commands = (
            Command.deserialize_commands(json["setup_command"])
            if "setup_command" in json
            else None
        )

        run_commands = Command.deserialize_commands(json["run_command"])

        cleanup_commands = (
            Command.deserialize_commands(json["cleanup_command"])
            if "cleanup_command" in json
            else None
        )

        stats: Command | dict[str, StatMatchInfo] = (
            Command.deserialize(json["stats"])
            if isinstance(json["stats"], str) or "command" in json["stats"]
            else {
                str(k): StatMatchInfo.deserialize(v) for k, v in json["stats"].items()
            }
        )

        return cls(
            json["name"],
            json["description"],
            setup_commands,
            run_commands,
            cleanup_commands,
            stats,
            json.get("virtualenv", False),
        )

    @classmethod
    def validate(cls, json: Any) -> None:
        """Validate a benchmark's json object."""
        from os.path import dirname, join
        from jsonschema import validate
        from json import load

        with open(
            join(dirname(__file__), "jsonschema", "benchmark.schema.json")
        ) as file:
            schema = load(file)
            validate(json, schema)


class Preset(Serializable):
    """
    Benchmark settings preset.

    Contains information on a single preset of benchmark settings.
    """

    def __init__(
        self,
        args: list[str] | str | None,
        init_commands: list[Command] | None = None,
        post_commands: list[Command] | None = None,
    ) -> None:
        """Create a benchmark Preset object."""
        from shlex import split

        if args is not None:
            self.args = args if isinstance(args, list) else split(args)
        elif init_commands is None:
            raise TypeError("Either args or init_command have to be specified")

        self.init_commands = init_commands
        self.post_commands = post_commands

    @classmethod
    def deserialize(cls, json: Any) -> Preset:
        if "args" not in json and "init_command" not in json:
            raise KeyError

        init_commands = (
            Command.deserialize_commands(json["init_command"])
            if "init_command" in json
            else None
        )

        post_commands = (
            Command.deserialize_commands(json["post_command"])
            if "post_command" in json
            else None
        )

        return cls(json.get("args", None), init_commands, post_commands)


class StatMatchInfo(Serializable):
    """Benchmark statistical data match info."""

    def __init__(self, regex: str, file: str | None = None) -> None:
        """Create a BenchmarkStat object."""
        self.regex = regex
        self.file = file

    @classmethod
    def deserialize(cls, json: Any) -> StatMatchInfo:
        return cls(**json)
