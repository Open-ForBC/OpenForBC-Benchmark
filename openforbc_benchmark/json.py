"""JSON module contains classes used for JSON (de)serialization."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

from abc import ABC, abstractmethod
from os.path import dirname, join
from jsonschema import validate
from json import load
from openforbc_benchmark.utils import Runnable


class Serializable(ABC):
    """
    A Serializable class can be serialized/deserialized into/from a JSON document.

    This abstract class provides methods to read/write such objects from/into a file.
    """

    @classmethod
    def serialize(cls, obj: Any) -> Any:
        """Serialize `obj` into a JSON object."""
        return obj.__dict__

    @classmethod
    @abstractmethod
    def deserialize(cls, json: Any) -> Serializable:
        """Deserialize instance from a JSON object."""
        pass

    def to_file(self, filename: str) -> None:
        """Serialize object as JSON into a file."""
        from json import dump

        with open(filename, "w") as file:
            dump(
                self.__class__.serialize(self),
                file,
                default=self.__class__.serialize,
            )

    @classmethod
    def from_file(cls, filename: str) -> Serializable:
        """Deserialize object as JSON from a file."""
        from json import load

        with open(filename, "r") as file:
            return cls.deserialize(load(file))


class BenchmarkInfo(Serializable):
    """A benchmark definition."""

    def __init__(
        self,
        name: str,
        description: str,
        setup_commands: list[CommandInfo] | None,
        run_commands: list[CommandInfo],
        cleanup_commands: list[CommandInfo] | None,
        stats: CommandInfo | dict[str, StatMatchInfo],
        virtualenv: bool,
    ) -> None:
        """Create a BenchmarkDefinition object."""
        self.name = name
        self.description = description
        self.setup_commands = setup_commands
        self.run_commands = run_commands
        self.cleanup_commands = cleanup_commands
        self.stats = stats
        self.virtualenv = virtualenv

    @classmethod
    def deserialize(cls, json: Any) -> BenchmarkInfo:
        cls.validate(json)

        setup_commands = (
            CommandInfo.deserialize_commands(json["setup_command"])
            if "setup_command" in json
            else None
        )

        run_commands = CommandInfo.deserialize_commands(json["run_command"])

        cleanup_commands = (
            CommandInfo.deserialize_commands(json["cleanup_command"])
            if "cleanup_command" in json
            else None
        )

        stats: CommandInfo | dict[str, StatMatchInfo] = (
            CommandInfo.deserialize(json["stats"])
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
        """Validate a benchmark definition json object."""
        with open(
            join(dirname(__file__), "jsonschema", "benchmark.schema.json")
        ) as file:
            schema = load(file)
            validate(json, schema)


class PresetInfo(Serializable):
    """
    Benchmark settings preset.

    Contains information on a single preset of benchmark settings.
    """

    def __init__(
        self,
        args: list[str] | str | None,
        init_commands: list[CommandInfo] | None = None,
        post_commands: list[CommandInfo] | None = None,
    ) -> None:
        """Create a benchmark Preset object."""
        from shlex import split

        self.args = None
        if args is not None:
            self.args = args if isinstance(args, list) else split(args)
        elif init_commands is None:
            raise TypeError("Either args or init_command have to be specified")

        self.init_commands = init_commands
        self.post_commands = post_commands

    @classmethod
    def deserialize(cls, json: Any) -> PresetInfo:
        cls.validate(json)

        if "args" not in json and "init_command" not in json:
            raise KeyError

        init_commands = (
            CommandInfo.deserialize_commands(json["init_command"])
            if "init_command" in json
            else None
        )

        post_commands = (
            CommandInfo.deserialize_commands(json["post_command"])
            if "post_command" in json
            else None
        )

        return cls(json.get("args", None), init_commands, post_commands)

    @classmethod
    def validate(cls, json: Any) -> None:
        """Validate a preset definition json object."""
        with open(
            join(dirname(__file__), "jsonschema", "benchmark_preset.schema.json")
        ) as file:
            schema = load(file)
            validate(json, schema)


class CommandInfo(Serializable):
    """
    A benchmark command which can be executed.

    Contains the command arguments and optionally some environment data.
    """

    def __init__(
        self,
        command: str | list[str],
        env: dict[str, str] = {},
        workdir: str | None = None,
    ) -> None:
        """Create a new command object."""
        from shlex import split

        if not isinstance(command, list):
            self.command = split(command)
        else:
            self.command = command

        self.env = env
        self.workdir = workdir

    def update(
        self,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        workdir: str | None = None,
    ) -> None:
        """Update command info."""
        if args is not None:
            self.command += args

        if env is not None:
            self.env.update(env)

        if workdir is not None:
            self.workdir = workdir

    def into_runnable(self) -> Runnable:
        """Create a Runnable object from this CommandInfo."""
        return Runnable(self.command, self.workdir, self.env)

    @classmethod
    def deserialize(cls, json: Any) -> CommandInfo:
        if isinstance(json, str):
            return cls(json)
        elif isinstance(json, dict):
            return cls(**json)
        else:
            assert False

    @classmethod
    def deserialize_commands(cls, json: Any) -> list[CommandInfo]:
        commands = [json] if not isinstance(json, list) else json

        return [CommandInfo.deserialize(c) for c in commands]


class StatMatchInfo(Serializable):
    """Benchmark statistical data match info."""

    def __init__(self, regex: str, file: str | None = None) -> None:
        """Create a StatMatchInfo object."""
        self.regex = regex
        self.file = file

    @classmethod
    def deserialize(cls, json: Any) -> StatMatchInfo:
        return cls(**json)


class BenchmarkStats(Serializable):
    """Benchmark statistical data."""

    def __init__(self, stats: dict[str, int | float]) -> None:
        """Create a BenchmarkStats object."""
        self.stats = stats

    @classmethod
    def deserialize(cls, json: Any) -> BenchmarkStats:
        cls.validate(json)

        if isinstance(json, dict):
            return cls(
                {
                    str(k): v
                    for k, v in filter(
                        lambda i: isinstance(i[1], (int, float)),
                        json.items(),
                    )
                }
            )

        return cls({})

    @classmethod
    def validate(cls, json: Any) -> None:
        """Validate a benchmark stats output json object."""
        with open(
            join(dirname(__file__), "jsonschema", "benchmark_preset.schema.json")
        ) as file:
            schema = load(file)
            validate(json, schema)
