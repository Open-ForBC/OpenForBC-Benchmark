from typer.testing import CliRunner

from openforbc_benchmark.cli.benchmark import app

runner = CliRunner()


def test_benchmark_default_command() -> None:
    """Default command must be `list -t`."""
    default_result = runner.invoke(app)
    assert default_result.exit_code == 0

    list_result = runner.invoke(app, ["list", "-t"])
    assert list_result.exit_code == 0

    assert default_result.stdout == list_result.stdout


def test_benchmark_list() -> None:
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "dummy_benchmark" in result.stdout

    table_result = runner.invoke(app, ["list", "-t"])
    assert table_result.exit_code == 0
    assert "---" in table_result.stdout
    assert "dummy_benchmark" in table_result.stdout
    assert "Dummy Benchmark" in table_result.stdout
    assert "Does nothing" in table_result.stdout
    assert "preset1" in table_result.stdout


def test_benchmark_presets() -> None:
    result = runner.invoke(app, ["presets", "dummy_benchmark"])
    assert result.exit_code == 0
    assert "preset1" in result.stdout
    assert "preset2" in result.stdout


def test_benchmark_run() -> None:
    result = runner.invoke(app, ["run", "dummy_benchmark"])
    assert result.exit_code == 0
    assert "---" in result.stdout
    assert "135246" in result.stdout
