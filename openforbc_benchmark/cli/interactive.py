# Copyright (c) 2021-2022 Istituto Nazionale di Fisica Nucleare
# SPDX-License-Identifier: MIT

from inquirer import list_input
from typer import Context, echo, Exit, Typer  # noqa: TC002

from openforbc_benchmark.benchmark import get_benchmarks
from openforbc_benchmark.cli.benchmark import CliBenchmarkRun
from openforbc_benchmark.cli.state import state
from openforbc_benchmark.cli.suite import (
    CliBenchmarkSuiteRun,
    get_suites,
    suite_definition_tool,
)


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
