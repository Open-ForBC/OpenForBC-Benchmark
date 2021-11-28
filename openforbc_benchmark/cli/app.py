from typer import Context, Option, Typer  # noqa: TC002

from openforbc_benchmark.cli.benchmark import app as benchmark_app
from openforbc_benchmark.cli.interactive import app as interactive_app
from openforbc_benchmark.cli.state import state

app = Typer()


@app.callback(invoke_without_command=True)
def callback(
    ctx: Context, search_path: str = Option(state["search_path"], envvar="O4BCB_PATH")
) -> None:
    state["search_path"] = search_path

    if ctx.invoked_subcommand is None:
        ctx.invoke(interactive_app)


app.add_typer(benchmark_app, name="benchmark")
app.add_typer(interactive_app, name="interactive")


def run() -> None:
    app()


if __name__ == "__main__":
    app()
