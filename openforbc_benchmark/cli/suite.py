from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Iterator, List, Optional, Tuple, Union

from sys import stdout
from typer import Context, echo, Exit, Typer, Option  # noqa: TC002

from openforbc_benchmark.benchmark import BenchmarkSuite
from openforbc_benchmark.cli.benchmark import CliBenchmarkRun
from openforbc_benchmark.cli.state import state


class CliBenchmarkSuiteRun:
    """A suite run in the CLI interface."""

    def __init__(
        self, suite: BenchmarkSuite, log_to_stderr: bool = not stdout.isatty()
    ) -> None:
        self.suite = suite
        self.stats: "List[Dict[str, Dict[str, Union[int, float]]]]" = []
        self._log_to_stderr = log_to_stderr

    def print_stats(self, json: bool = False) -> None:
        from json import dumps
        from tabulate import tabulate

        if json:
            return echo(dumps(self.stats))

        for i, run_stats in enumerate(self.stats):
            table: "List[Tuple[str, str, Union[int, float]]]" = []
            echo()
            echo(f"RUN#{i + 1} - {self.suite.benchmark_runs[i].benchmark.name}")
            for preset, preset_stats in run_stats.items():
                table.extend(
                    (preset, stat, value) for stat, value in preset_stats.items()
                )

            echo(tabulate(table, ["Preset", "Stat", "Value"]))

    def start(self) -> None:
        for i, bench_run in enumerate(self.suite.benchmark_runs):
            echo(f"Running benchmark run #{i + 1}", err=self._log_to_stderr)
            run = CliBenchmarkRun(bench_run, self._log_to_stderr)
            run.start()
            self.stats.append(run.stats)


def get_suites(search_path: str) -> "Iterator[BenchmarkSuite]":
    """Get all the suites in the search path."""
    from os import listdir
    from os.path import isfile, join

    for dir in [join(x, "suites") for x in search_path.split(":")]:
        for file in listdir(dir):
            path = join(dir, file)
            if isfile(path) and file.endswith(".json"):
                yield BenchmarkSuite.from_definition_file(path, search_path)


def find_suite(search: str, search_path: str) -> "Optional[BenchmarkSuite]":
    """Find a benchmark suite by its name or part of it (matching the first one)."""
    return next(
        (suite for suite in get_suites(search_path) if suite.name.startswith(search)),
        None,
    )


app = Typer(help="List, inspect and run benchmark suites")


@app.command("list")
def list_suites(table: bool = Option(False, "--table", "-t")) -> None:
    """List available suites in the search path."""
    from tabulate import tabulate
    from textwrap import shorten

    suites = get_suites(state["search_path"])
    echo(
        tabulate(
            (
                (suite.name, shorten(suite.description, 40, placeholder="..."))
                for suite in suites
            ),
            headers=["Name", "Description"],
            tablefmt="simple",
        )
        if table
        else "\n".join(suite.name for suite in suites)
    )


@app.command("get")
def get_suite_info(suite_name: str) -> None:
    """Get suite information."""
    from tabulate import tabulate

    suite = find_suite(suite_name, state["search_path"])
    if suite is None:
        echo(f'ERROR: Suite "{suite_name}" not found in search path')
        raise Exit(1)

    echo(f"name: {suite.name}")
    echo(f"description: {suite.description}")
    echo()
    echo(
        tabulate(
            [
                (run.benchmark.name, ", ".join(preset.name for preset in run.presets))
                for run in suite.benchmark_runs
            ],
            headers=["Benchmark", "Presets"],
            tablefmt="simple",
        )
    )


@app.command("run")
def run_suite(suite_name: str, json: bool = Option(False, "--json", "-j")) -> None:
    """Run the specified suite."""
    suite = find_suite(suite_name, state["search_path"])
    if suite is None:
        echo(f'ERROR: Suite "{suite_name}" not found in search path')
        raise Exit(1)

    run = CliBenchmarkSuiteRun(suite)
    run.start()
    run.print_stats(json)


@app.callback(invoke_without_command=True)
def default(ctx: Context) -> None:
    if ctx.invoked_subcommand is None:
        ctx.invoke(list_suites, True)
