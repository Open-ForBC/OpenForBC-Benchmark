from sys import stdout
from typer import Context, echo, Exit, Typer, Option  # noqa: TC002
from typing import TYPE_CHECKING

from openforbc_benchmark.benchmark import BenchmarkSuite, get_benchmarks
from openforbc_benchmark.json import BenchmarkRunDefinition, BenchmarkSuiteDefinition
from openforbc_benchmark.cli.benchmark import CliBenchmarkRun
from openforbc_benchmark.cli.state import state

if TYPE_CHECKING:
    from typing import Dict, Iterator, List, Optional, Tuple, Union
    from openforbc_benchmark.benchmark import Benchmark


class CliBenchmarkSuiteRun:
    """A suite run in the CLI interface."""

    def __init__(
        self, suite: BenchmarkSuite, log_to_stderr: bool = not stdout.isatty()
    ) -> None:
        """Create a CliBenchmarkSuiteRun."""
        self.suite = suite
        self.stats: "List[Dict[str, Dict[str, Union[int, float]]]]" = []
        self._log_to_stderr = log_to_stderr

    def print_stats(self, json: bool = False) -> None:
        """Print benchmark suite's stats."""
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
        """Run this benchmark suite."""
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


def prompt_benchmark_run(benchmarks: "List[Benchmark]") -> BenchmarkRunDefinition:
    """Prompt the user to define a benchmark run."""
    from inquirer import checkbox, list_input

    benchmark_name = list_input(
        "Select the benchmark", choices=[benchmark.get_id() for benchmark in benchmarks]
    )
    benchmark = next(
        benchmark for benchmark in benchmarks if benchmark.get_id() == benchmark_name
    )

    presets = benchmark.get_presets()
    selected_preset_names = checkbox(
        "Select some presets (select with <spacebar>)",
        choices=[preset.name for preset in presets],
        default=benchmark.get_default_preset().name,
    )

    if not selected_preset_names:
        echo("ERROR: No preset selected", err=True)
        raise Exit(1)

    selected_presets = [
        preset for preset in presets if preset.name in selected_preset_names
    ]

    if not selected_presets:
        echo(
            "ERROR: Couldn't find any of presets \""
            f'{", ".join(selected_preset_names)}"',
            err=True,
        )
        raise Exit(1)

    return BenchmarkRunDefinition(
        benchmark.get_id(), [preset.name for preset in presets]
    )


def suite_definition_tool() -> None:
    """Interactively create a suite definition."""
    from inquirer import confirm, text
    from json import dumps
    from os.path import exists, join

    benchmarks = list(get_benchmarks(state["search_path"]))

    suite_name = text("Suite name")
    suite_description = text("Suite description")

    benchmark_runs: "List[BenchmarkRunDefinition]" = []

    while True:
        benchmark_runs.append(prompt_benchmark_run(benchmarks))
        if not confirm("Do you want to add another benchmark run?"):
            break

    suite = BenchmarkSuiteDefinition(suite_name, suite_description, benchmark_runs)

    json = dumps(suite, indent=2, default=suite.serialize)
    echo("Previewing JSON...")
    echo(json)

    if confirm("Save definition to suites folder?", default=True):
        while True:
            filename = text("filename (.json will be added if missing)")

            if not filename:
                echo("Filename can't be empty!")
                continue

            if not filename.endswith(".json"):
                filename += ".json"

            path = join("suites", filename)

            if exists(path) and not confirm("File already exists, overwrite?"):
                continue

            with open(path, "w") as file:
                file.write(json)

            break


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


@app.command("create")
def create_suite() -> None:
    """Create a suite interactively."""
    return suite_definition_tool()


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
