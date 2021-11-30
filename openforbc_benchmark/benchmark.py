from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Dict, Iterator, List, Optional, Tuple, Union
    from openforbc_benchmark.json import StatMatchInfo

from typing import TextIO

from openforbc_benchmark.json import (
    BenchmarkInfo,
    BenchmarkStats,
    CommandInfo,
    PresetInfo,
)
from openforbc_benchmark.utils import Runnable


class Benchmark(BenchmarkInfo):
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
    def from_definition(self_class, definition: BenchmarkInfo, dir: str) -> "Benchmark":
        return self_class(**definition.__dict__, dir=dir)

    @classmethod
    def from_definition_file(self_class, path: str) -> "Benchmark":
        """Build a Benchmark object from the definiton path."""
        from os.path import dirname

        return self_class.from_definition(BenchmarkInfo.from_file(path), dirname(path))

    def get_id(self) -> str:
        """Get benchmark ID (folder basename)."""
        from os.path import basename

        return basename(self.dir)

    def get_presets(self) -> "List[Preset]":
        """Get benchmark preset names."""
        from os import listdir
        from os.path import basename, join

        presets_dir = join(self.dir, "presets")
        return [
            Preset(basename(file)[:-5], PresetInfo.from_file(join(presets_dir, file)))
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

        return Preset(
            name[:-5] if name.endswith(".json") else name,
            PresetInfo.from_file(join(presets_dir, filename)),
        )

    def run(self, presets: "List[Preset]") -> "BenchmarkRun":
        """Create a `BenchmarkRun` for this benchmark."""
        return BenchmarkRun(self, presets)


class Preset:  # noqa: SIM119
    def __init__(self, name: str, definition: PresetInfo) -> None:
        self.name = name
        self.definition = definition


class BenchmarkRun:
    """
    A single Benchmark run session.

    Contains multiple presets.
    """

    def __init__(self, benchmark: "Benchmark", presets: "List[Preset]") -> None:
        self.benchmark = benchmark
        self.presets = presets
        self.virtualenv: "Optional[str]" = None

    def setup(self) -> "Iterator[Runnable]":
        """Get tasks for this benchmark run setup commands."""
        from os.path import join

        if self.benchmark.virtualenv:
            yield self._add_context(Runnable(["python3", "-m", "venv", ".venv"]))
            self.virtualenv = join(self.benchmark.dir, ".venv")

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
        definition = preset.definition
        if definition.init_commands is not None:
            for command in definition.init_commands:
                yield self._add_context(command.into_runnable())

        for command in self.benchmark.run_commands:
            yield self._add_context(
                (
                    command.extend(definition.args)
                    if definition.args is not None
                    else command
                ).into_runnable()
            )

        if definition.post_commands is not None:
            for command in definition.post_commands:
                yield self._add_context(command.into_runnable())

    def _add_context(self, runnable: Runnable) -> Runnable:
        from os.path import isabs, join

        run_env = runnable.env.copy() if runnable.env is not None else None
        if self.virtualenv is not None:
            new_env = {
                "VIRTUALENV": self.virtualenv,
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
            [join(self.virtualenv, "bin")] if self.virtualenv is not None else [],
        )
