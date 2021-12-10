from typer import Context, echo, Exit, Typer  # noqa: TC002

from openforbc_benchmark.benchmark import get_benchmarks
from openforbc_benchmark.cli.benchmark import CliBenchmarkRun
from openforbc_benchmark.cli.state import state
from openforbc_benchmark.cli.suite import CliBenchmarkSuiteRun, get_suites

app = Typer()


@app.callback(invoke_without_command=True)
def callback(ctx: Context) -> None:
    if ctx.invoked_subcommand is None:
        ctx.invoke(interactive_prompt)


@app.command()
def interactive_prompt() -> None:
    from inquirer import checkbox, list_input

    command = list_input(
        "Do you want to run a suite or a single benchmark?",
        choices=["Suite", "Single benchmark"],
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

        selected_preset_names = checkbox(
            "Chose some presets", choices=[preset.name for preset in presets]
        )

        selected_presets = [
            preset for preset in presets if preset.name in selected_preset_names
        ]

        if not selected_presets:
            echo("ERROR: No preset selected", err=True)
            raise Exit(1)

        run = benchmark.run(selected_presets)
        cli_run = CliBenchmarkRun(run)
        cli_run.start()
        cli_run.print_stats()
