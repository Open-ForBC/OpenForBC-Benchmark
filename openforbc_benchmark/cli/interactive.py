from typer import Context, echo, Exit, Typer  # noqa: TC002

from openforbc_benchmark.cli.benchmark import (
    CliBenchmarkRun,
    print_stats,
    search_benchmarks,
)

app = Typer()


@app.callback(invoke_without_command=True)
def callback(ctx: Context) -> None:
    if ctx.invoked_subcommand is None:
        ctx.invoke(interactive_prompt)


@app.command()
def interactive_prompt() -> None:
    from inquirer import checkbox, list_input

    benchmarks = list(search_benchmarks())

    answer = list_input(
        "Chose a benchmark",
        choices=[benchmark.get_id() for benchmark in benchmarks],
    )

    benchmark = next(
        benchmark for benchmark in benchmarks if benchmark.get_id() == answer
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
    stats = CliBenchmarkRun(run).start()

    print_stats(stats, False)
