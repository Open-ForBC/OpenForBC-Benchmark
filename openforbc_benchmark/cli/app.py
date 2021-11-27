from typer import Option, Typer

from openforbc_benchmark.cli.benchmark import app as benchmark_app
from openforbc_benchmark.cli.state import state

app = Typer()


@app.callback(invoke_without_command=True)
def callback(
    search_path: str = Option(state["search_path"], envvar="O4BCB_PATH")
) -> None:
    state["search_path"] = search_path


app.add_typer(benchmark_app, name="benchmark")


def run() -> None:
    app()


if __name__ == "__main__":
    app()
