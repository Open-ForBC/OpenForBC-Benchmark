from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Dict, Iterator, List, Optional, Tuple, Union
    from openforbc_benchmark.json import StatMatchInfo

from typing import TextIO

from openforbc_benchmark.json import (
    BenchmarkDefinition,
    BenchmarkStats,
    CommandInfo,
    PresetDefinition,
)
from openforbc_benchmark.utils import Runnable


class Benchmark(BenchmarkDefinition):
    """A benchmark."""

    def __init__(
        self,
        name: str,
        description: str,
        setup_commands: "Optional[List[CommandInfo]]",
        run_commands: "List[CommandInfo]",
        cleanup_commands: "Optional[List[CommandInfo]]",
        stats: "Union[CommandInfo, Dict[str, StatMatchInfo]]",
        virtualenv: bool,
        dir: str,
    ) -> None:
        """Create a Benchmark object."""
        super().__init__(
            name,
            description,
            setup_commands,
            run_commands,
            cleanup_commands,
            stats,
            virtualenv,
        )
        self.dir = dir

    @classmethod
    def from_definition(
        self_class, definition: BenchmarkDefinition, dir: str
    ) -> "Benchmark":
        return self_class(**definition.__dict__, dir=dir)

    @classmethod
    def from_definition_file(self_class, path: str) -> "Benchmark":
        """Build a Benchmark object from the definiton path."""
        from os.path import dirname

        return self_class.from_definition(
            BenchmarkDefinition.from_file(path), dirname(path)
        )

    def get_id(self) -> str:
        """Get benchmark ID (folder basename)."""
        from os.path import basename

        return basename(self.dir)

    def get_presets(self) -> "List[Preset]":
        """Get benchmark preset names."""
        from os import listdir
        from os.path import join

        presets_dir = join(self.dir, "presets")
        return [
            Preset.from_definition_file(join(presets_dir, file))
            for file in listdir(presets_dir)
            if file.endswith(".json")
        ]

    def get_preset(self, name: str) -> "Optional[Preset]":
        """Retrieve benchmark preset."""
        from os.path import exists, join

        presets_dir = join(self.dir, "presets")

        filename = name if name.endswith(".json") else name + ".json"
        if not exists(join(presets_dir, filename)):
            return None

        return Preset.from_definition_file(join(presets_dir, filename))

    def run(self, presets: "List[Preset]") -> "BenchmarkRun":
        """Create a `BenchmarkRun` for this benchmark."""
        return BenchmarkRun(self, presets)


class Preset(PresetDefinition):
    def __init__(
        self,
        name: str,
        args: "Optional[Union[List[str], str]]",
        init_commands: "Optional[List[CommandInfo]]" = None,
        env: "Dict[str, str]" = {},
        post_commands: "Optional[List[CommandInfo]]" = None,
    ) -> None:
        super().__init__(args, init_commands, env, post_commands)
        self.name = name

    @classmethod
    def from_definition(
        self_class, definition: PresetDefinition, name: str
    ) -> "Preset":
        return self_class(name, **definition.__dict__)

    @classmethod
    def from_definition_file(self_class, path: str) -> "Preset":
        from os.path import basename

        filename = basename(path)

        name = filename[:-5] if filename.endswith(".json") else filename
        return self_class.from_definition(PresetDefinition.from_file(path), name)


class BenchmarkRun:
    """
    A single Benchmark run session.

    Contains multiple presets.
    """

    def __init__(self, benchmark: "Benchmark", presets: "List[Preset]") -> None:
        self.benchmark = benchmark
        self.presets = presets
        self._virtualenv: "Optional[str]" = None

    def setup(self) -> "Iterator[Runnable]":
        """Get tasks for this benchmark run setup commands."""
        from os.path import join

        if self.benchmark.virtualenv:
            yield self._add_context(Runnable(["python3", "-m", "venv", ".venv"]))
            self._virtualenv = join(self.benchmark.dir, ".venv")

        if self.benchmark.setup_commands is not None:
            for command in self.benchmark.setup_commands:
                yield self._add_context(command.into_runnable())

    def run(self) -> "Iterator[Tuple[Preset, Iterator[Runnable]]]":
        """
        Get tasks for each selected preset.

        Returns an Iterator into tuples containing:
        - a Preset: the current preset
        - a Iterator into `Runnable`s: the preset's tasks
        """
        for preset in self.presets:
            yield preset, self._run_preset(preset)

    def get_stats(self, stdout: "Union[str, TextIO]") -> "Dict[str, Union[int, float]]":
        from json import load, loads
        from jsonschema import validate
        from os.path import dirname, join
        from re import compile
        from subprocess import PIPE, run

        if isinstance(self.benchmark.stats, CommandInfo):
            p = run(
                **self._add_context(
                    self.benchmark.stats.into_runnable()
                ).into_popen_args(),
                stderr=PIPE,
                stdout=PIPE
            )
            json = loads(p.stdout.decode())
            schema_path = join(dirname(__file__), "jsonschema", "benchmark.schema.json")
            with open(schema_path, "r") as schema_file:
                schema = load(schema_file)
                validate(json, schema)
            return BenchmarkStats.deserialize(json).stats

        stats: "Dict[str, Union[int, float]]" = {}
        for name, match in self.benchmark.stats.items():
            file = stdout
            if match.file is not None:
                file = open(join(self.benchmark.dir, match.file), "r")  # noqa: SIM115

            regex = compile(match.regex)
            for line in file if not isinstance(file, str) else file.splitlines():
                m = regex.search(line)
                if m is not None:
                    number = m.group(1)
                    stats[name] = float(number) if "." in number else int(number)
                    break

            if match.file is not None and isinstance(file, TextIO):
                file.close()

        return stats

    def cleanup(self) -> "Iterator[Runnable]":
        """Get cleanup tasks for this benchmark."""
        if self.benchmark.cleanup_commands is not None:
            for command in self.benchmark.cleanup_commands:
                yield self._add_context(command.into_runnable())

    def _run_preset(self, preset: "Preset") -> "Iterator[Runnable]":
        """Get tasks for the selected preset."""
        if preset.init_commands is not None:
            for command in preset.init_commands:
                yield self._add_context(command.into_runnable())

        for command in self.benchmark.run_commands:
            yield self._add_context(
                (
                    command.extend(preset.args, preset.env)
                    if preset.args is not None
                    else command
                ).into_runnable()
            )

        if preset.post_commands is not None:
            for command in preset.post_commands:
                yield self._add_context(command.into_runnable())

    def _add_context(self, runnable: Runnable) -> Runnable:
        from os.path import isabs, join

        run_env = runnable.env.copy() if runnable.env is not None else None
        if self._virtualenv is not None:
            new_env = {
                "VIRTUALENV": self._virtualenv,
            }

            if run_env is not None:
                run_env.update(new_env)
            else:
                run_env = new_env

        cwd = (
            (
                runnable.cwd
                if isabs(runnable.cwd)
                else join(self.benchmark.dir, runnable.cwd)
            )
            if runnable.cwd is not None
            else self.benchmark.dir
        )

        return Runnable(
            runnable.args,
            cwd,
            run_env,
            [join(self._virtualenv, "bin")] if self._virtualenv is not None else [],
        )


def get_benchmarks(search_path: str) -> "Iterator[Benchmark]":
    """Get all the benchmarks in the search path."""
    from os import listdir
    from os.path import exists, join

    for path in [join(x, "benchmarks") for x in search_path.split(":")]:
        try:
            for dir in listdir(path):
                if exists(join(path, dir, "benchmark.json")):
                    yield Benchmark.from_definition_file(
                        join(path, dir, "benchmark.json")
                    )
        except (FileNotFoundError, NotADirectoryError):
            continue


def find_benchmark(id: str, search_path: str) -> "Optional[Benchmark]":
    """Find a benchmark by ID in the search path."""
    return next((x for x in get_benchmarks(search_path) if x.get_id() == id), None)
