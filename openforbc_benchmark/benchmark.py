from typing import TYPE_CHECKING

from openforbc_benchmark.json import (
    BenchmarkDefinition,
    BenchmarkStats,
    BenchmarkSuiteDefinition,
    CommandInfo,
    PresetDefinition,
)
from openforbc_benchmark.utils import Runnable

if TYPE_CHECKING:
    from typing import Dict, Iterator, List, Optional, TextIO, Tuple, Union
    from openforbc_benchmark.json import BenchmarkRunDefinition, StatMatchInfo


class BenchmarkNotFound(Exception):
    pass


class BenchmarkPresetNotFound(Exception):
    pass


class BenchmarkStatsError(Exception):
    pass


class BenchmarkStatsDecodeError(BenchmarkStatsError):
    def __init__(self, message: str, output: str) -> None:
        super().__init__(message)
        self.output = output


class BenchmarkStatsMatchError(BenchmarkStatsError):
    pass


class Benchmark(BenchmarkDefinition):
    """
    A benchmark instance.

    This class wraps a `BenchmarkDefinition` adding a `dir` (benchmark's
    containing directory) field and provides additional methods to extract
    information from the defintion.
    """

    def __init__(
        self,
        name: str,
        description: str,
        default_preset: str,
        test_preset: "Optional[str]",
        setup_commands: "Optional[List[CommandInfo]]",
        run_commands: "List[CommandInfo]",
        cleanup_commands: "Optional[List[CommandInfo]]",
        test_commands: "List[CommandInfo]",
        stats: "Union[CommandInfo, Dict[str, StatMatchInfo]]",
        virtualenv: bool,
        dir: str,
    ) -> None:
        """Create a Benchmark object."""
        super().__init__(
            name,
            description,
            default_preset,
            test_preset,
            setup_commands,
            run_commands,
            cleanup_commands,
            test_commands,
            stats,
            virtualenv,
        )
        self.dir = dir

    @classmethod
    def from_definition(
        self_class, definition: BenchmarkDefinition, dir: str
    ) -> "Benchmark":
        """Create a Benchmark from a definition and its containing directory path."""
        return self_class(**definition.__dict__, dir=dir)

    def into_definition(self) -> BenchmarkDefinition:
        """Transform this Benchmark into a defintion."""
        return BenchmarkDefinition(
            self.name,
            self.description,
            self.default_preset,
            self.test_preset,
            self.setup_commands,
            self.run_commands,
            self.cleanup_commands,
            self.test_commands,
            self.stats,
            self.virtualenv,
        )

    @classmethod
    def from_definition_file(self_class, path: str) -> "Benchmark":
        """Create a Benchmark object from its definiton file path."""
        from os.path import dirname

        return self_class.from_definition(
            BenchmarkDefinition.from_file(path), dirname(path)
        )

    def get_id(self) -> str:
        """Get benchmark ID (folder basename)."""
        from os.path import basename

        return basename(self.dir)

    def get_presets(self) -> "List[Preset]":
        """Get benchmark presets' names."""
        from os import listdir
        from os.path import join

        presets_dir = join(self.dir, "presets")
        return [
            Preset.from_definition_file(join(presets_dir, file))
            for file in listdir(presets_dir)
            if file.endswith(".json")
        ]

    def get_default_preset(self) -> "Preset":
        """Get benchmark's default preset."""
        default = self.get_preset(self.default_preset)
        if default is None:
            raise BenchmarkPresetNotFound(
                f'Default preset "{self.default_preset}" not found for benchmark '
                f'"{self.name}"'
            )
        return default

    def get_test_preset(self) -> "Optional[Preset]":
        """Get benchmark's test preset."""
        return self.get_preset(self.test_preset) if self.test_preset else None

    def get_preset(self, name: str) -> "Optional[Preset]":
        """Get (eventually) benchmark's preset by name."""
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
        """Create a Preset from a definition and a name."""
        return self_class(name, **definition.__dict__)

    def into_definition(self) -> PresetDefinition:
        """Transform benchmark into a definition."""
        return PresetDefinition(
            self.args, self.init_commands, self.env, self.post_commands
        )

    @classmethod
    def from_definition_file(self_class, path: str) -> "Preset":
        """Create a Preset from its definition file path."""
        from os.path import basename

        filename = basename(path)

        name = filename[:-5] if filename.endswith(".json") else filename
        return self_class.from_definition(PresetDefinition.from_file(path), name)


class BenchmarkSuite:
    """
    A suite of benchmarks, each with their own presets.

    This class doesn't extend `BenchmarkSuiteDefinition`, while still having a
    class method which allows to instantiate an instance from a definition by
    providing a search path for the benchmarks.
    """

    def __init__(
        self, name: str, description: str, benchmark_runs: "List[BenchmarkRun]"
    ) -> None:
        """Create a BenchmarkSuite."""
        self.name = name
        self.description = description
        self.benchmark_runs = benchmark_runs

    @classmethod
    def from_definition(
        self_class, definition: BenchmarkSuiteDefinition, search_path: str
    ) -> "BenchmarkSuite":
        """Create a BenchmarkSuite from its definition and a benchmark search path."""
        return self_class(
            definition.name,
            definition.description,
            [
                BenchmarkRun.from_definition(bench_run_def, search_path)
                for bench_run_def in definition.benchmark_runs
            ],
        )

    @classmethod
    def from_definition_file(
        self_class, path: str, search_path: str
    ) -> "BenchmarkSuite":
        """
        Create a BenchmarkSuite from its definition file's path.

        A benchmark search path must also be specified.
        """
        return self_class.from_definition(
            BenchmarkSuiteDefinition.from_file(path), search_path
        )


class BenchmarkRun:
    """
    A single Benchmark run session.

    Consists of a Benchmark with an associated list of `Preset`s.
    """

    def __init__(self, benchmark: "Benchmark", presets: "List[Preset]") -> None:
        """Create a BenchmarkRun."""
        self.benchmark = benchmark
        self.presets = presets
        self._virtualenv: "Optional[str]" = None

    @classmethod
    def from_definition(
        self_class, definition: "BenchmarkRunDefinition", search_path: str
    ) -> "BenchmarkRun":
        """Create a BenchmarkRun from its definition and a benchmarks search path."""
        benchmark = find_benchmark(definition.benchmark_folder, search_path)
        if benchmark is None:
            raise BenchmarkNotFound(
                f'Benchmark "{definition.benchmark_folder}" not found in search path '
                f'"{search_path}"'
            )

        selected_presets = []
        presets = benchmark.get_presets()
        for name in definition.presets:
            if name.endswith(".json"):
                name = name[:-5]
            try:
                selected_presets.append(
                    # Try to find preset with matching name (will raise `StopIteration`
                    # if no match is found)
                    next(preset for preset in presets if preset.name == name)
                )
            except StopIteration:
                raise BenchmarkPresetNotFound(
                    f'Preset "{name}" not found for benchmark "{benchmark.name}"'
                ) from None

        return self_class(benchmark, selected_presets)

    def setup(self) -> "Iterator[Runnable]":
        """Get tasks for this benchmark run setup commands."""
        from os.path import join

        # (Eventually) create a virtualenv for the benchmark
        if self.benchmark.virtualenv:
            yield self._add_context(Runnable(["python3", "-m", "venv", ".venv"]))
            self._virtualenv = join(self.benchmark.dir, ".venv")

        if self.benchmark.setup_commands is not None:
            for command in self.benchmark.setup_commands:
                yield self._add_context(command.into_runnable())

    def run(self) -> "Iterator[Tuple[Preset, Iterator[Runnable]]]":
        """
        Get tasks for each selected preset.

        :returns: an Iterator into tuples containing:
            - a Preset: the current preset
            - a Iterator into `Runnable`s: the preset's tasks
        """
        for preset in self.presets:
            yield preset, self._run_preset(preset)

    def test(self) -> "Iterator[Runnable]":
        """Get the tasks for this benchmark run's test commands."""
        for command in self.benchmark.test_commands:
            yield self._add_context(command.into_runnable())

    def get_stats(self, stdout: "Union[str, TextIO]") -> "Dict[str, Union[int, float]]":
        """
        Parse stats out of benchmark's standard output.

        :param stdout: benchmark's output as a file or file path.
        :returns: dictionary of stat name and stat value (int or float).
        :raises BenchmarkStatsDecodeError: if the stats script's json output couldn't be
            parsed correctly.
        :raises BenchmarkStatsMatchError: if a stat's regex couldn't match any line in
            the benchmark's output.
        """
        from json import load, loads
        from json.decoder import JSONDecodeError
        from jsonschema import validate, ValidationError
        from os.path import abspath, dirname, join
        from re import compile
        from subprocess import PIPE, run

        if isinstance(self.benchmark.stats, CommandInfo):
            # Run benchmark's stats script passing stdout file name as first argument
            p = run(
                **self._add_context(
                    self.benchmark.stats.extend(
                        [
                            abspath(stdout)
                            if isinstance(stdout, str)
                            else abspath(stdout.name)
                        ]
                    ).into_runnable()
                ).into_popen_args(),
                stderr=PIPE,
                stdout=PIPE,
            )
            stats_output = p.stdout.decode()

            try:
                json = loads(stats_output)
            except JSONDecodeError as e:
                raise BenchmarkStatsDecodeError(
                    f"Failed to decode stats script json output: {e}", stats_output
                ) from None

            # Validate stats script output against stats jsonschema (should prevent
            # further errors when deserializing)
            schema_path = join(
                dirname(__file__), "jsonschema", "benchmark_stats.schema.json"
            )
            with open(schema_path, "r") as schema_file:
                schema = load(schema_file)
                try:
                    validate(json, schema)
                except ValidationError as e:
                    raise BenchmarkStatsDecodeError(
                        f"Decoded output from stats script is not valid: {e}",
                        stats_output,
                    )

            return BenchmarkStats.deserialize(json).stats

        stats: "Dict[str, Union[int, float]]" = {}
        for name, match in self.benchmark.stats.items():

            file = (
                open(stdout, "r") if isinstance(stdout, str) else stdout  # noqa: SIM115
            )

            if match.file is not None:
                file = open(join(self.benchmark.dir, match.file), "r")  # noqa: SIM115

            # (Try to) match regex agains every line in the file
            regex = compile(match.regex)
            for line in file if not isinstance(file, str) else file.splitlines():
                m = regex.search(line)
                if m is not None:
                    number = m.group(1)
                    stats[name] = float(number) if "." in number else int(number)
                    break

            if name not in stats:
                raise BenchmarkStatsMatchError(
                    f'No match for stat "{name}" in benchmark output'
                )

            if file is not stdout:
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

        last = len(self.benchmark.run_commands) - 1
        for i, command in enumerate(self.benchmark.run_commands):
            yield self._add_context(
                (
                    # Add preset arguments only to last run command
                    command.extend(preset.args, preset.env)
                    if i == last and preset.args is not None
                    else command
                ).into_runnable()
            )

        if preset.post_commands is not None:
            for command in preset.post_commands:
                yield self._add_context(command.into_runnable())

    def _add_context(self, runnable: Runnable) -> Runnable:
        """
        Populate command context with this run's environment.

        Will add benchmark's directory as cwd and (eventually) set up a python virtualenv
        to isolate this benchmark.
        """
        from os.path import isabs, join

        run_env = runnable.env.copy() if runnable.env is not None else None
        if self._virtualenv is not None:
            new_env = {
                "VIRTUAL_ENV": self._virtualenv,
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
            # Add virtualenv's bin directory to PATH
            [join(self._virtualenv, "bin")] if self._virtualenv is not None else [],
        )


def get_benchmarks(search_path: str) -> "Iterator[Benchmark]":
    """
    Get all the benchmarks in the search path.

    :param search_path: colon separated list of directories in which to search for
        benchmarks.
    """
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
    """
    Find a benchmark by ID in the search path.

    :param id: id of the benchmark (directory name)
    :param search_path: colon separated list of directories in which to search for
        benchmarks.
    """
    return next((x for x in get_benchmarks(search_path) if x.get_id() == id), None)
