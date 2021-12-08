from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Any, Dict, Tuple, Union
    from openforbc_benchmark.benchmark import Benchmark, BenchmarkRun
    from openforbc_benchmark.utils import Runnable

from typer import Context, echo, Exit, Typer, Option  # noqa: TC002
from typing import List  # noqa: TC002
from yaspin.core import Yaspin

from openforbc_benchmark.benchmark import find_benchmark, get_benchmarks
from openforbc_benchmark.cli.state import state
from openforbc_benchmark.utils import argv_join


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

    def __init__(self, benchmark_run: "BenchmarkRun") -> None:
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

    def start(self) -> "Dict[str, Dict[str, Union[int, float]]]":
        with self.spinner:
            return self._start()

    def _start(self) -> "Dict[str, Dict[str, Union[int, float]]]":
        from os.path import join
        from json.decoder import JSONDecodeError
        from jsonschema import ValidationError

        benchmark_id = self.benchmark_run.benchmark.get_id()

        self.spinner.write(f'Running "{benchmark_id}" setup commands')
        for i, task in enumerate(self.benchmark_run.setup()):
            self.spinner.text = f"{benchmark_id}(setup): {argv_join(task.args)}"
            self._run_task_or_err(
                task,
                join(self.log_dir, f"setup.{i + 1}"),
                f'Benchmark "{benchmark_id}" setup command "{argv_join(task.args)}" '
                "failed",
            )

        stats = {}
        for preset, tasks in self.benchmark_run.run():
            self.spinner.write(f'Running "{benchmark_id}" preset "{preset.name}"')
            for i, task in enumerate(tasks):
                self.spinner.text = (
                    f"{benchmark_id}(run:{preset.name}): {argv_join(task.args)}"
                )
                self._run_task_or_err(
                    task,
                    join(self.log_dir, f"run_{preset.name}.{i + 1}"),
                    f'Benchmark "{benchmark_id}" preset "{preset.name}" command '
                    f'"{argv_join(task.args)}" failed',
                )
                last_task_i = i

            with open(
                join(self.log_dir, f"run_{preset.name}.{last_task_i + 1}.out.log"), "r"
            ) as output:
                next(output)

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

    def _print(self, message: "Any", err: bool = False) -> None:
        with self.spinner.hidden():
            echo(message, err=err)

    def _run_task_or_err(
        self, task: "Runnable", log_prefix: str, err_message: "Any"
    ) -> None:
        try:
            ret = self._run_task(task, log_prefix)
        except Exception as e:
            self._print(err_message, True)
            self._fail(BenchmarkTaskError(f"Task {task} did not start because of {e}"))

        if ret != 0:
            self._print(err_message, True)
            self._fail(
                BenchmarkTaskFailed(f"Task {task} failed with return code {ret}")
            )

    def _run_task(self, task: "Runnable", log_prefix: str) -> int:
        from selectors import DefaultSelector, EVENT_READ
        from subprocess import PIPE, Popen
        from time import sleep
        from typing import cast, IO

        self.spinner.write(f"$ {argv_join(task.args)}")

        proc = Popen(**task.into_popen_args(), stderr=PIPE, stdout=PIPE)
        assert proc.stdout is not None
        assert proc.stderr is not None

        outsel = DefaultSelector()
        outsel.register(proc.stdout, EVENT_READ)
        outsel.register(proc.stderr, EVENT_READ)

        with outsel, open(f"{log_prefix}.err.log", "w") as err_log, open(
            f"{log_prefix}.out.log", "w"
        ) as out_log:
            err_log.write(f"$ {argv_join(task.args)}\n")
            out_log.write(f"$ {argv_join(task.args)}\n")

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

                    log_file = err_log if k.fileobj is proc.stderr else out_log
                    log_file.write(
                        line.decode() if line.endswith(b"\n") else line.decode() + "\n"
                    )

        while proc.poll() is None:
            sleep(0.05)

        return proc.returncode


def get_benchmark_log_dir(benchmark: "Benchmark") -> str:
    """Get log directory for a benchmark."""
    from os import getcwd, mkdir
    from os.path import exists, join

    log_dir = join(getcwd(), "logs")

    if not exists(log_dir):
        mkdir(log_dir)
        echo(
            'WARNING: Log directory "logs" not found in current directory, creating it',
            err=True,
        )

    return join(getcwd(), "logs", benchmark.get_id())


def print_stats(
    stats: "Dict[str, Dict[str, Union[int, float]]]", json: bool = True
) -> None:
    from json import dumps
    from tabulate import tabulate

    if json:
        return echo(dumps(stats))

    table: "List[Tuple[str, str, Union[int, float]]]" = []
    for preset, preset_stats in stats.items():
        table.extend((preset, stat, value) for stat, value in preset_stats.items())

    echo(tabulate(table, ["Preset", "Stat", "Value"]))


app = Typer()


@app.command("list")
def list_benchmarks(table: bool = Option(False, "--table", "-t")) -> None:
    from tabulate import tabulate
    from textwrap import shorten

    benchmarks = get_benchmarks(state["search_path"])

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
    benchmark = find_benchmark(benchmark_id, state["search_path"])
    if benchmark is None:
        echo(f'ERROR: Benchmark "{benchmark_id}" not found in search path')
        raise Exit(1)
    presets = benchmark.get_presets()

    echo("\n".join(preset.name for preset in presets))


@app.command("run")
def run_benchmark(
    benchmark_id: str,
    preset_names: "List[str]",  # noqa: TC201
    table: bool = Option(False, "--table", "-t"),
) -> None:
    preset_names = list(preset_names)  # https://github.com/tiangolo/typer/issues/127

    benchmark = find_benchmark(benchmark_id, state["search_path"])
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
