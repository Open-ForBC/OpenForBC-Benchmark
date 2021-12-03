"""JSON module contains classes used for JSON (de)serialization."""

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Union

from abc import ABC as AbstractClass, abstractmethod
from os.path import dirname, join
from jsonschema import validate
from json import load
from openforbc_benchmark.utils import Runnable

T = TypeVar("T", bound="Serializable")


class Serializable(AbstractClass, Generic[T]):
    """
    A Serializable class can be serialized/deserialized into/from a JSON document.

    This abstract class provides methods to read/write such objects from/into a file.
    """

    @classmethod
    def serialize(self_class, obj: "Any") -> "Any":
        """Serialize `obj` into a JSON object."""
        return obj.__dict__

    @classmethod
    @abstractmethod
    def deserialize(self_class, json: "Any") -> T:
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
    def from_file(self_class, filename: str) -> T:
        """Deserialize object as JSON from a file."""
        from json import load

        with open(filename, "r") as file:
            return self_class.deserialize(load(file))


class BenchmarkInfo(Serializable["BenchmarkInfo"]):
    """A benchmark definition."""

    def __init__(
        self,
        name: str,
        description: str,
        setup_commands: "Optional[List[CommandInfo]]",
        run_commands: "List[CommandInfo]",
        cleanup_commands: "Optional[List[CommandInfo]]",
        stats: "Union[CommandInfo, Dict[str, StatMatchInfo]]",
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
    def deserialize(self_class, json: "Any") -> "BenchmarkInfo":
        self_class.validate(json)

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

        stats: "Union[CommandInfo , Dict[str, StatMatchInfo]]" = (
            CommandInfo.deserialize(json["stats"])
            if isinstance(json["stats"], str) or "command" in json["stats"]
            else {
                str(k): StatMatchInfo.deserialize(v) for k, v in json["stats"].items()
            }
        )

        return self_class(
            json["name"],
            json["description"],
            setup_commands,
            run_commands,
            cleanup_commands,
            stats,
            json.get("virtualenv", False),
        )

    @classmethod
    def validate(self_class, json: "Any") -> None:
        """Validate a benchmark definition json object."""
        with open(
            join(dirname(__file__), "jsonschema", "benchmark.schema.json")
        ) as file:
            schema = load(file)
            validate(json, schema)


class PresetInfo(Serializable["PresetInfo"]):
    """
    Benchmark settings preset.

    Contains information on a single preset of benchmark settings.
    """

    def __init__(
        self,
        args: "Optional[Union[List[str], str]]",
        init_commands: "Optional[List[CommandInfo]]" = None,
        env: "Dict[str, str]" = {},
        post_commands: "Optional[List[CommandInfo]]" = None,
    ) -> None:
        """Create a benchmark Preset object."""
        from shlex import split

        self.args = None
        if args is not None:
            self.args = args if isinstance(args, list) else split(args)
        elif init_commands is None:
            raise TypeError("Either args or init_command have to be specified")

        self.env = env

        self.init_commands = init_commands
        self.post_commands = post_commands

    @classmethod
    def deserialize(self_class, json: "Any") -> "PresetInfo":
        self_class.validate(json)

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

        return self_class(
            json.get("args", None), init_commands, json.get("env", {}), post_commands
        )

    @classmethod
    def validate(self_class, json: "Any") -> None:
        """Validate a preset definition json object."""
        with open(
            join(dirname(__file__), "jsonschema", "benchmark_preset.schema.json")
        ) as file:
            schema = load(file)
            validate(json, schema)


class CommandInfo(Serializable["CommandInfo"]):
    """
    A benchmark command which can be executed.

    Contains the command arguments and optionally some environment data.
    """

    def __init__(
        self,
        command: "Union[List[str], str]",
        env: "Dict[str, str]" = {},
        workdir: "Optional[str]" = None,
    ) -> None:
        """Create a new command object."""
        from shlex import split

        if not isinstance(command, list):
            self.command = split(command)
        else:
            self.command = command

        self.env = env
        self.workdir = workdir

    def extend(
        self,
        args: "Optional[List[str]]" = None,
        env: "Optional[Dict[str, str]]" = None,
        workdir: "Optional[str]" = None,
    ) -> "CommandInfo":
        """Create an extended version of this command."""
        new_env = self.env.copy()
        if env is not None:
            new_env.update(env)

        return CommandInfo(
            self.command + args if args is not None else self.command,
            new_env,
            workdir if workdir is not None else self.workdir,
        )

    def into_runnable(self) -> Runnable:
        """Create a Runnable object from this CommandInfo."""
        return Runnable(self.command, self.workdir, self.env)

    @classmethod
    def deserialize(self_class, json: "Any") -> "CommandInfo":
        if isinstance(json, str):
            return self_class(json)
        elif isinstance(json, dict):
            return self_class(**json)
        else:
            assert False

    @classmethod
    def deserialize_commands(self_class, json: "Any") -> "List[CommandInfo]":
        commands = [json] if not isinstance(json, list) else json

        return [CommandInfo.deserialize(c) for c in commands]


class StatMatchInfo(Serializable["StatMatchInfo"]):
    """Benchmark statistical data match info."""

    def __init__(self, regex: str, file: "Optional[str]" = None) -> None:
        """Create a StatMatchInfo object."""
        self.regex = regex
        self.file = file

    @classmethod
    def deserialize(self_class, json: "Any") -> "StatMatchInfo":
        return self_class(**json)


class BenchmarkStats(Serializable["BenchmarkStats"]):
    """Benchmark statistical data."""

    def __init__(self, stats: "Dict[str, Union[int, float]]") -> None:
        """Create a BenchmarkStats object."""
        self.stats = stats

    @classmethod
    def deserialize(self_class, json: "Any") -> "BenchmarkStats":
        self_class.validate(json)

        if isinstance(json, dict):
            return self_class(
                {
                    str(k): v
                    for k, v in filter(
                        lambda i: isinstance(i[1], (int, float)),
                        json.items(),
                    )
                }
            )

        return self_class({})

    @classmethod
    def validate(self_class, json: "Any") -> None:
        """Validate a benchmark stats output json object."""
        with open(
            join(dirname(__file__), "jsonschema", "benchmark_preset.schema.json")
        ) as file:
            schema = load(file)
            validate(json, schema)
