from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Any, Iterator
    from openforbc_benchmark.benchmark import BenchmarkRun
    from openforbc_benchmark.utils import Runnable

from typer import Context, echo, Exit, Typer, Option  # noqa: TC002
from yaspin.core import Yaspin

from openforbc_benchmark.benchmark import Benchmark
from openforbc_benchmark.cli.state import state


class BenchmarkRunException(Exception):
    pass


class BenchmarkTaskError(BenchmarkRunException):
    """The task failed to start."""

    pass


class BenchmarkTaskFailed(BenchmarkRunException):
    """The task has failed (return code != 0)."""

    pass


class BenchmarkValidationError(BenchmarkRunException):
    """Stats decode failed."""

    pass


class CliBenchmarkRun:
    """A benchmark run in the CLI interface."""

    def __init__(self, benchmark_run: BenchmarkRun) -> None:
        from datetime import datetime
        from os import mkdir
        from os.path import dirname, exists, join

        self.benchmark_run = benchmark_run
        self.spinner = Yaspin()
        self.log_dir = join(
            get_benchmark_log_dir(benchmark_run.benchmark),
            datetime.now().strftime("%Y%m%d_%H%M%S"),
        )

        parent = dirname(self.log_dir)
        if not exists(parent):
            mkdir(parent)

        mkdir(self.log_dir)

    def start(self) -> dict[str, dict[str, int | float]]:
        with self.spinner:
            return self._start()

    def _start(self) -> dict[str, dict[str, int | float]]:
        from json.decoder import JSONDecodeError
        from jsonschema import ValidationError
        from shlex import join

        benchmark_id = self.benchmark_run.benchmark.get_id()

        self.spinner.write(f'Running "{benchmark_id}" setup commands')
        for task in self.benchmark_run.setup():
            self.spinner.text = f"{benchmark_id}(setup): {join(task.args)}"
            self._run_task_or_err(
                task,
                self._get_log_path("setup"),
                f'Benchmark "{benchmark_id}" setup command "{join(task.args)}" failed',
            )

        stats = {}
        for preset, tasks in self.benchmark_run.run():
            self.spinner.write(f'Running "{benchmark_id}" preset "{preset.name}"')
            for task in tasks:
                self.spinner.text = (
                    f"{benchmark_id}(run:{preset.name}): {join(task.args)}"
                )
                self._run_task_or_err(
                    task,
                    self._get_log_path(f"run_{preset.name}"),
                    f'Benchmark "{benchmark_id}" preset "{preset.name}" command '
                    f'"{join(task.args)}" failed',
                )

            with open(self._get_log_path(f"run_{preset.name}"), "r") as output:
                try:
                    stats[preset.name] = self.benchmark_run.get_stats(output)
                except (JSONDecodeError, ValidationError) as e:
                    self._print(
                        f'Failed to decode stats for preset "{preset.name}"', err=True
                    )
                    self._fail(
                        BenchmarkValidationError(
                            f'"{benchmark_id}" preset "{preset.name}" stats decode '
                            f"failed: {e}"
                        ),
                    )

        return stats

    def _fail(self, exception: BenchmarkRunException) -> None:
        self.spinner.stop()

        echo(exception)
        echo(f'ERROR: Benchmark "{self.benchmark_run.benchmark.get_id()}" failed')
        raise Exit(1)

    def _get_log_path(self, identifier: str) -> str:
        from os.path import join

        return join(self.log_dir, f"{identifier}.log")

    def _print(self, message: Any, err: bool = False) -> None:
        with self.spinner.hidden():
            echo(message, err=err)

    def _run_task_or_err(self, task: Runnable, log_path: str, err_message: Any) -> None:
        try:
            ret = self._run_task(task, log_path)
        except Exception as e:
            self._print(err_message, True)
            self._fail(BenchmarkTaskError(f"Task {task} did not start because of {e}"))

        if ret != 0:
            self._print(err_message, True)
            self._fail(
                BenchmarkTaskFailed(f"Task {task} failed with return code {ret}")
            )

    def _run_task(self, task: Runnable, log_path: str) -> int:
        from selectors import DefaultSelector, EVENT_READ
        from shlex import join
        from subprocess import PIPE, Popen
        from time import sleep
        from typing import cast, IO

        self.spinner.write(f"$ {join(task.args)}")

        proc = Popen(**task.into_popen_args(), stderr=PIPE, stdout=PIPE)
        assert proc.stdout is not None
        assert proc.stderr is not None

        outsel = DefaultSelector()
        outsel.register(proc.stdout, EVENT_READ)
        outsel.register(proc.stderr, EVENT_READ)

        with outsel, open(log_path, "a") as log_file:
            reading = True
            while reading:
                for k, _ in outsel.select():
                    line = cast(IO[bytes], k.fileobj).readline()
                    if not line:
                        outsel.unregister(k.fileobj)
                        if not outsel.get_map():
                            reading = False
                        continue

                    self.spinner.write(line.rstrip().decode())

                    if k.fileobj is proc.stdout:
                        log_file.write(
                            line.decode()
                            if line.endswith(b"\n")
                            else line.decode() + "\n"
                        )

        while proc.poll() is None:
            sleep(0.05)

        return proc.returncode


def search_benchmarks() -> Iterator[Benchmark]:
    """Search benchmarks in the search path."""
    from os import listdir
    from os.path import exists, join

    for path in [join(x, "benchmarks") for x in state["search_path"].split(":")]:
        try:
            for dir in listdir(path):
                if exists(join(path, dir, "benchmark.json")):
                    yield Benchmark.from_definition_file(
                        join(path, dir, "benchmark.json")
                    )
        except (FileNotFoundError, NotADirectoryError):
            echo(f'ERROR: Path "{path}" in search path is not a directory', err=True)


def find_benchmark(id: str) -> Benchmark | None:
    """Find a benchmark by ID in the search path."""
    return next((x for x in search_benchmarks() if x.get_id() == id), None)


def get_benchmark_log_dir(benchmark: Benchmark) -> str:
    """Get log directory for a benchmark."""
    from os import getcwd
    from os.path import exists, join

    log_dir = join(getcwd(), "logs")

    if not exists(log_dir):
        echo('ERROR: Log directory "logs" not found in current directory', err=True)
        raise Exit(1)

    return join(getcwd(), "logs", benchmark.get_id())


def print_stats(stats: dict[str, dict[str, int | float]], json: bool = True) -> None:
    from json import dumps
    from tabulate import tabulate

    if json:
        return echo(dumps(stats))

    table: list[tuple[str, str, int | float]] = []
    for preset, preset_stats in stats.items():
        table.extend((preset, stat, value) for stat, value in preset_stats.items())

    echo(tabulate(table, ["Preset", "Stat", "Value"]))


app = Typer()


@app.command("list")
def list_benchmarks(table: bool = Option(False, "--table", "-t")) -> None:
    from tabulate import tabulate
    from textwrap import shorten

    benchmarks = search_benchmarks()

    echo(
        tabulate(
            map(
                lambda benchmark: (
                    benchmark.get_id(),
                    benchmark.name,
                    shorten(benchmark.description, 40, placeholder="..."),
                ),
                benchmarks,
            ),
            headers=["ID", "Name", "Description"],
            tablefmt="simple",
        )
        if table
        else "\n".join(map(lambda bench: bench.get_id(), benchmarks))
    )


@app.command("presets")
def list_presets(benchmark_id: str) -> None:
    benchmark = find_benchmark(benchmark_id)
    if benchmark is None:
        echo(f'ERROR: Benchmark "{benchmark_id}" not found in search path')
        raise Exit(1)
    presets = benchmark.get_presets()

    echo("\n".join(preset.name for preset in presets))


@app.command("run")
def run_benchmark(
    benchmark_id: str,
    preset_names: list[str],
    table: bool = Option(False, "--table", "-t"),
) -> None:
    preset_names = list(preset_names)  # https://github.com/tiangolo/typer/issues/127

    benchmark = find_benchmark(benchmark_id)
    if benchmark is None:
        echo(f'ERROR: Benchmark "{benchmark_id}" not found in search path')
        raise Exit(1)
    presets = []
    for name in preset_names:
        preset = benchmark.get_preset(name)
        if preset is None:
            echo(f'ERROR: Preset "{name}" not found in benchmark "{benchmark_id}"')
            raise Exit(1)
        presets.append(preset)
    run = benchmark.run(presets)

    stats = CliBenchmarkRun(run).start()

    print_stats(stats, not table)


@app.callback(invoke_without_command=True)
def default(ctx: Context) -> None:
    if ctx.invoked_subcommand is None:
        ctx.invoke(list_benchmarks, False)
