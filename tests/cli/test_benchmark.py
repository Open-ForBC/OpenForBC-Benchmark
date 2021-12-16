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


def test_benchmark_list_presets() -> None:
    result_table = runner.invoke(app, ["list-presets", "dummy_benchmark"])
    assert result_table.exit_code == 0
    assert "---" in result_table.stdout
    assert "preset1" in result_table.stdout
    assert "preset2" in result_table.stdout

    result_no_table = runner.invoke(app, ["list-presets", "-T", "dummy_benchmark"])
    assert result_no_table.exit_code == 0
    assert "---" not in result_no_table.stdout
    assert "preset1" in result_no_table.stdout
    assert "preset2" in result_no_table.stdout


def test_benchmark_get_preset() -> None:
    result = runner.invoke(app, ["get-preset", "dummy_benchmark", "preset1"])
    assert result.exit_code == 0
    assert all(x in result.stdout for x in ("preset1", "Dummy Benchmark"))
    assert all(x in result.stdout for x in ("echo data: 135246", "echo setup.sh"))


def test_benchmark_get() -> None:
    result = runner.invoke(app, ["get", "dummy_benchmark"])
    assert result.exit_code == 0
    assert all(x in result.stdout for x in ("Dummy Benchmark", "Does nothing"))
    assert all(
        x in result.stdout
        for x in ("echo 'hello world'", "echo data: 135246", "echo daw")
    )
    assert "Virtualenv: disabled" in result.stdout


def test_benchmark_run() -> None:
    result = runner.invoke(app, ["run", "dummy_benchmark"])
    assert result.exit_code == 0
    assert "---" in result.stdout
    assert "135246" in result.stdout


def test_benchmark_test() -> None:
    result = runner.invoke(app, ["test", "dummy_benchmark"])
    assert result.exit_code == 0
    assert "true" in result.stdout
