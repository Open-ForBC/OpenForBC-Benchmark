from json import dumps
from tabulate import tabulate
from os.path import join
from sys import stdout
from typer import Context, echo, Exit, Typer, Option  # noqa: TC002
from typer.params import Argument
from typing import List  # noqa: TC002
from typing import TYPE_CHECKING
from yaspin.core import Yaspin

from openforbc_benchmark.benchmark import (
    BenchmarkPresetNotFound,
    BenchmarkStatsDecodeError,
    BenchmarkStatsMatchError,
    find_benchmark,
    get_benchmarks,
)
from openforbc_benchmark.cli.state import state
from openforbc_benchmark.json import CommandInfo
from openforbc_benchmark.utils import argv_join

if TYPE_CHECKING:
    from typing import Any, Dict, Tuple, Union
    from openforbc_benchmark.benchmark import Benchmark, BenchmarkRun, Preset
    from openforbc_benchmark.json import StatMatchInfo
    from openforbc_benchmark.utils import Runnable


class BenchmarkRunException(Exception):
    pass


class BenchmarkTaskError(BenchmarkRunException):
    """The task failed to start."""

    pass


class BenchmarkTaskFailed(BenchmarkRunException):
    """The task has failed (return code != 0)."""

    pass


class BenchmarkRunStatsError(BenchmarkRunException):
    """Stats decode failed."""

    pass


class CliBenchmarkRun:
    """A benchmark run in the CLI interface."""

    def __init__(
        self, benchmark_run: "BenchmarkRun", log_to_stderr: bool = not stdout.isatty()
    ) -> None:
        from datetime import datetime
        from os import mkdir
        from os.path import dirname, exists

        self.benchmark_run = benchmark_run
        self.spinner = Yaspin()
        self.log_dir = join(
            get_benchmark_log_dir(benchmark_run.benchmark),
            datetime.now().strftime("%Y%m%d_%H%M%S"),
        )
        self.stats: "Dict[str, Dict[str, Union[int, float]]]" = {}
        self._log_to_stderr = log_to_stderr

        parent = dirname(self.log_dir)
        if exists(self.log_dir):
            i = 1
            while exists(f"{self.log_dir}.{i}"):
                i += 1
            self.log_dir = f"{self.log_dir}.{i}"
        elif not exists(parent):
            mkdir(parent)

        mkdir(self.log_dir)

    def print_stats(self, json: bool = False) -> None:
        """Print benchmark stats to output."""
        if json:
            return echo(dumps(self.stats))

        table: "List[Tuple[str, str, Union[int, float]]]" = []
        for preset, preset_stats in self.stats.items():
            table.extend((preset, stat, value) for stat, value in preset_stats.items())

        echo(tabulate(table, ["Preset", "Stat", "Value"]))

    def start(self, test_only: bool = False) -> None:
        """Run the benchmark (interface method)."""
        if self._log_to_stderr:
            self._run_setup()
            self._run_test() if test_only else self._run()
        else:
            with self.spinner:
                self._run_setup()
                self._run_test() if test_only else self._run()

    def _run(self) -> None:
        """Run the benchmark."""
        benchmark_id = self.benchmark_run.benchmark.get_id()

        for preset, tasks in self.benchmark_run.run():
            self._log(f'Running "{benchmark_id}" preset "{preset.name}"')
            for i, task in enumerate(tasks):
                from os import get_terminal_size
                from textwrap import shorten

                self.spinner.text = shorten(
                    f"{benchmark_id}(run:{preset.name}): {argv_join(task.args)}",
                    # spinner uses 2 chars
                    (get_terminal_size().columns if stdout.isatty() else 80) - 2,
                    placeholder="...",
                )
                self._run_task_or_err(
                    task,
                    join(self.log_dir, f"run_{preset.name}.{i + 1}"),
                    f'Benchmark "{benchmark_id}" preset "{preset.name}" command '
                    f'"{argv_join(task.args)}" failed',
                )
                last_task_i = i

            out_filename = join(
                self.log_dir, f"run_{preset.name}.{last_task_i + 1}.out.log"
            )

            try:
                if isinstance(self.benchmark_run.benchmark.stats, CommandInfo):
                    self.stats[preset.name] = self.benchmark_run.get_stats(out_filename)
                else:
                    with open(out_filename, "r") as output:
                        next(output)
                        self.stats[preset.name] = self.benchmark_run.get_stats(output)
            except BenchmarkStatsDecodeError as e:
                self._log("ERROR: stats script output:", err=True)
                self._log(e.output.rstrip(), err=True)
                self._fail(
                    BenchmarkRunStatsError(
                        f'"{benchmark_id}" preset "{preset.name}" stats decode '
                        f"failed: {e}"
                    ),
                )
            except BenchmarkStatsMatchError as e:
                self._fail(
                    BenchmarkRunStatsError(
                        f'"{benchmark_id}" preset "{preset.name}" stats match failed: '
                        f"{e}"
                    )
                )

    def _run_setup(self) -> None:
        """Run benchmark's setup tasks."""
        benchmark_id = self.benchmark_run.benchmark.get_id()

        self._log(f'Running "{benchmark_id}" setup commands')
        for i, task in enumerate(self.benchmark_run.setup()):
            self.spinner.text = f"{benchmark_id}(setup): {argv_join(task.args)}"
            self._run_task_or_err(
                task,
                join(self.log_dir, f"setup.{i + 1}"),
                f'Benchmark "{benchmark_id}" setup command "{argv_join(task.args)}" '
                "failed",
            )

    def _run_test(self) -> None:
        """Run benchmark's test tasks."""
        benchmark_id = self.benchmark_run.benchmark.get_id()

        self._log(f'Running "{benchmark_id}" test commands')
        for i, task in enumerate(self.benchmark_run.test()):
            self.spinner.text = f"{benchmark_id}(test): {argv_join(task.args)}"
            self._run_task_or_err(
                task,
                join(self.log_dir, f"setup.{i + 1}"),
                f'Benchmark "{benchmark_id}" test command "{argv_join(task.args)}" '
                "failed",
            )

    def _fail(self, exception: BenchmarkRunException) -> None:
        """
        Terminate the execution printing an exception into stderr.

        :param exception: exception that caused the failure.
        """
        self.spinner.stop()

        echo(exception, err=True)
        if isinstance(exception, BenchmarkRunStatsError):
            echo(
                f"WARNING: Stats decode for benchmark "
                f'"{self.benchmark_run.benchmark.get_id()}" failed',
                err=True,
            )
            return

        echo(
            f'ERROR: Benchmark "{self.benchmark_run.benchmark.get_id()}" failed',
            err=True,
        )
        raise Exit(1)

    def _log(self, message: "Any", err: bool = True) -> None:
        """
        Log a message to stdout/err.

        :param message: message to log.
        :param err: `True` to use stderr, `False` for stdout.
        """
        with self.spinner.hidden():
            echo(message, err=(self._log_to_stderr or err))

    def _run_task_or_err(
        self, task: "Runnable", log_prefix: str, err_message: "Any"
    ) -> None:
        """
        Run a task, eventually failing with an exception.

        :param task: the task to run.
        :param log_prefix: output filename prefix.
        :param err_message: error message to be shown when the task fails.
        """
        try:
            ret = self._run_task(task, log_prefix)
        except Exception as e:
            self._log(err_message, err=True)
            self._fail(BenchmarkTaskError(f"Task {task} did not start because of {e}"))

        if ret != 0:
            if ret == 1 and "venv" in task.args:
                with open(f"{log_prefix}.err.log", "r") as output:
                    if "Error: [Errno 2] No such file or directory:" in output.read():
                        self._log(
                            "WARNING: Possibly broken symbolic link in benchmark's "
                            f"virtualenv ({self.benchmark_run.benchmark.dir}/.venv), "
                            "delete it and try again",
                            err=True,
                        )
                pass

            self._log(err_message, err=True)
            self._fail(
                BenchmarkTaskFailed(f"Task {task} failed with return code {ret}")
            )

    def _run_task(self, task: "Runnable", log_prefix: str) -> int:
        """Run the task."""
        from selectors import DefaultSelector, EVENT_READ
        from subprocess import PIPE, Popen
        from time import sleep
        from typing import cast, IO

        self._log(task)

        proc = Popen(**task.into_popen_args(), stderr=PIPE, stdout=PIPE)
        assert proc.stdout is not None
        assert proc.stderr is not None

        # Selector to read from both stdout and stderr
        outsel = DefaultSelector()
        outsel.register(proc.stdout, EVENT_READ)
        outsel.register(proc.stderr, EVENT_READ)

        with outsel, open(f"{log_prefix}.err.log", "w") as err_log, open(
            f"{log_prefix}.out.log", "w"
        ) as out_log:
            err_log.write(f"{task}\n")
            out_log.write(f"{task}\n")

            reading = True
            while reading:
                for k, _ in outsel.select():
                    # Try to read a line from either stdout or stderr
                    line = cast(IO[bytes], k.fileobj).readline()
                    if not line:
                        # Unregister ended fileobj
                        outsel.unregister(k.fileobj)
                        if not outsel.get_map():  # No more output
                            reading = False
                        continue

                    self._log(line.rstrip().decode())

                    # Write line to err/out log file
                    log_file = err_log if k.fileobj is proc.stderr else out_log
                    log_file.write(
                        line.decode() if line.endswith(b"\n") else line.decode() + "\n"
                    )

        while proc.poll() is None:
            sleep(0.05)

        return proc.returncode


def find_benchmark_or_fail(benchmark_id: str) -> "Benchmark":
    """Search for a benchmark in the search path or fail with an error."""
    benchmark = find_benchmark(benchmark_id, state["search_path"])
    if benchmark is None:
        echo(f'ERROR: Benchmark "{benchmark_id}" not found in search path')
        raise Exit(1)

    return benchmark


def get_preset_or_fail(benchmark: "Benchmark", preset_name: str) -> "Preset":
    """Get benchmark's preset by name or fail with an error message."""
    preset = benchmark.get_preset(preset_name)
    if preset is None:
        echo(
            f'ERROR: Preset "{preset_name}" not found in benchmark '
            f'"{benchmark.get_id()}"'
        )
        raise Exit(1)

    return preset


def get_benchmark_log_dir(benchmark: "Benchmark") -> str:
    """Get log directory for a benchmark."""
    from os import getcwd, mkdir
    from os.path import exists

    log_dir = join(getcwd(), "logs")

    if not exists(log_dir):
        mkdir(log_dir)
        echo(
            'WARNING: Log directory "logs" not found in current directory, creating it',
            err=True,
        )

    return join(getcwd(), "logs", benchmark.get_id())


def pretty_commands(commands: List[CommandInfo]) -> str:
    """Prettify command representation."""
    return "\n".join(f"\t{command.into_runnable()}" for command in commands)


def pretty_stats(stats: "Union[CommandInfo, Dict[str, StatMatchInfo]]") -> str:
    """Prettify benchmark stats data."""
    if isinstance(stats, dict):
        return "\n".join(
            f'\t{k}: /{v.regex}/ @ {v.file if v.file else "stdout"}'
            for k, v in stats.items()
        )

    return pretty_commands([stats])


app = Typer(help="List, inspect and run benchmark and presets")


@app.command("list")
def list_benchmarks(table: bool = Option(False, "--table", "-t")) -> None:
    """List benchmarks in the search path."""
    from textwrap import shorten

    benchmarks = get_benchmarks(state["search_path"])

    echo(
        tabulate(
            map(
                lambda benchmark: (
                    benchmark.get_id(),
                    shorten(benchmark.name, 20, placeholder="..."),
                    shorten(benchmark.description, 40, placeholder="..."),
                    benchmark.default_preset,
                ),
                benchmarks,
            ),
            headers=["ID", "Name", "Description", "Default preset"],
            tablefmt="simple",
        )
        if table
        else "\n".join(map(lambda bench: bench.get_id(), benchmarks))
    )


@app.command("list-presets")
def list_presets(
    benchmark_folder: str, table: bool = Option(True, "--table/--no-table", "-t/-T")
) -> None:
    """List benchmark's presets."""
    benchmark = find_benchmark_or_fail(benchmark_folder)
    if benchmark is None:
        echo(f'ERROR: Benchmark "{benchmark_folder}" not found in search path')
        raise Exit(1)

    presets = benchmark.get_presets()

    echo(
        tabulate(
            [
                (preset.name, argv_join(preset.args) if preset.args else None)
                for preset in presets
            ],
            headers=["Name", "Args"],
        )
        if table
        else "\n".join(preset.name for preset in presets)
    )


@app.command("get-preset")
def preset_info(
    benchmark_folder: str, preset_name: str, json: bool = Option(False, "--json", "-j")
) -> None:
    """Get information for a benchmark preset."""
    benchmark = find_benchmark_or_fail(benchmark_folder)
    preset = get_preset_or_fail(benchmark, preset_name)

    if json:
        definition = preset.into_definition()
        return echo(dumps(definition, default=definition.serialize, indent=2))

    echo(
        f'Preset "{preset_name}" - "{benchmark.name}"\n'
        "Final benchmark run command:\n"
        f"\t{benchmark.run_commands[-1].extend(preset.args, preset.env).into_runnable()}"
        "\n"
        + (
            f"Init commands:\n{pretty_commands(preset.init_commands)}\n"
            if preset.init_commands
            else ""
        )
        + (
            f"Post commands:\n{pretty_commands(preset.post_commands)}\n"
            if preset.post_commands
            else ""
        ),
        nl=False,
    )


@app.command("get")
def benchmark_info(
    benchmark_folder: str, json: bool = Option(False, "--json", "-j")
) -> None:
    """Get benchmark information."""
    benchmark = find_benchmark_or_fail(benchmark_folder)

    if json:
        definition = benchmark.into_definition()
        return echo(dumps(definition, default=definition.serialize, indent=2))

    echo(
        f"{benchmark.name} - {benchmark.description}\n"
        f"Default preset: {benchmark.default_preset}\n"
        + (
            f"Setup commands:\n{pretty_commands(benchmark.setup_commands)}\n"
            if benchmark.setup_commands
            else ""
        )
        + f"Run commands:\n{pretty_commands(benchmark.run_commands)}\n"
        + (
            f"Cleanup commands:\n{pretty_commands(benchmark.cleanup_commands)}\n"
            if benchmark.cleanup_commands
            else ""
        )
        + f"Stats:\n{pretty_stats(benchmark.stats)}\n"
        + f"Virtualenv: {'enabled' if benchmark.virtualenv else 'disabled'}"
    )


@app.command("run")
def run_benchmark(
    benchmark_folder: str,
    preset_names: "List[str]" = Argument(None),  # noqa: TC201
    use_test_preset: bool = Option(False, "--test-preset", "-t"),
    json: bool = Option(False, "--json", "-j"),
) -> None:
    """Run specified benchmark with one or more presets."""
    # typer has a bug and arguments specified as lists get passed as tuples
    # see: https://github.com/tiangolo/typer/issues/127
    preset_names = list(preset_names)

    benchmark = find_benchmark_or_fail(benchmark_folder)

    presets = []
    if use_test_preset:
        test_preset = benchmark.get_test_preset()
        try:
            presets.append(
                test_preset if test_preset else benchmark.get_default_preset()
            )
        except BenchmarkPresetNotFound as e:
            echo(f"ERROR: {e}")
            raise Exit(1) from None
        if test_preset:
            presets.append(test_preset)
    elif not preset_names:
        try:
            presets.append(benchmark.get_default_preset())
        except BenchmarkPresetNotFound as e:
            echo(f"ERROR: {e}")
            raise Exit(1) from None
    else:
        for name in preset_names:
            preset = get_preset_or_fail(benchmark, name)
            presets.append(preset)

    run = benchmark.run(presets)

    cli_run = CliBenchmarkRun(run)
    cli_run.start()
    cli_run.print_stats(json)


@app.command("test")
def test_benchmark(benchmark_folder: str) -> None:
    """Run test commands for the specified benchmark."""
    benchmark = find_benchmark_or_fail(benchmark_folder)

    CliBenchmarkRun(benchmark.run([])).start(test_only=True)


@app.callback(invoke_without_command=True)
def default(ctx: Context) -> None:
    if ctx.invoked_subcommand is None:
        ctx.invoke(list_benchmarks, True)
