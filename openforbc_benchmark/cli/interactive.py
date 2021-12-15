from typing import TYPE_CHECKING

from openforbc_benchmark.json import (
    BenchmarkRunDefinition,
    BenchmarkSuiteDefinition,
)

if TYPE_CHECKING:
    from typing import List
    from openforbc_benchmark.benchmark import Benchmark

from inquirer import list_input
from typer import Context, echo, Exit, Typer  # noqa: TC002

from openforbc_benchmark.benchmark import get_benchmarks
from openforbc_benchmark.cli.benchmark import CliBenchmarkRun
from openforbc_benchmark.cli.state import state
from openforbc_benchmark.cli.suite import CliBenchmarkSuiteRun, get_suites


def prompt_benchmark_run(benchmarks: "List[Benchmark]") -> "BenchmarkRunDefinition":
    from inquirer import checkbox

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


app = Typer(help="Run interactive prompt")


@app.callback(invoke_without_command=True)
def callback(ctx: Context) -> None:
    if ctx.invoked_subcommand is None:
        ctx.invoke(interactive_prompt)


@app.command()
def interactive_prompt() -> None:
    command = list_input(
        "Do you want to run a suite or a single benchmark?",
        choices=["Suite", "Single benchmark", "Create suite"],
    )

    if command == "Suite":
        suites = list(get_suites(state["search_path"]))

        suite_name = list_input(
            "Chose a suite", choices=[suite.name for suite in suites]
        )

        suite = next(suite for suite in suites if suite.name == suite_name)

        suite_run = CliBenchmarkSuiteRun(suite)
        suite_run.start()
        suite_run.print_stats()

    elif command == "Single benchmark":
        benchmarks = list(get_benchmarks(state["search_path"]))

        benchmark_id = list_input(
            "Chose a benchmark",
            choices=[benchmark.get_id() for benchmark in benchmarks],
        )

        benchmark = next(
            benchmark for benchmark in benchmarks if benchmark.get_id() == benchmark_id
        )

        presets = benchmark.get_presets()
        default_preset = benchmark.get_default_preset()

        preset_name = list_input(
            "Chose a preset",
            choices=[preset.name for preset in presets],
            default=[default_preset.name],
        )

        preset = next(preset for preset in presets if preset.name == preset_name)

        if not preset:
            echo(
                "ERROR: Couldn't find the selected preset (this is a bug).",
                err=True,
            )
            raise Exit(1)

        run = benchmark.run([preset])
        cli_run = CliBenchmarkRun(run)
        cli_run.start()
        cli_run.print_stats()

    elif command == "Create suite":
        suite_definition_tool()
