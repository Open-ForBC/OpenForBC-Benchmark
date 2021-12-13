from typer.testing import CliRunner

from openforbc_benchmark.cli.suite import app

runner = CliRunner()


def test_suite_default_command() -> None:
    default = runner.invoke(app)
    assert default.exit_code == 0
    list = runner.invoke(app, ["list", "-t"])
    assert list.exit_code == 0

    assert default.stdout == list.stdout


def test_suite_list() -> None:
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Dummy benchmark suite" in result.stdout

    table_result = runner.invoke(app, ["list", "-t"])
    assert table_result.exit_code == 0
    assert "---" in table_result.stdout
    assert "Dummy benchmark suite" in table_result.stdout
    assert "A preconfigured collection" in table_result.stdout


def test_suite_info() -> None:
    result = runner.invoke(app, ["get", "Dummy benchmark suite"])
    assert result.exit_code == 0
    assert "name: Dummy benchmark suite" in result.stdout
    assert "description: A preconfigured" in result.stdout
    assert "---" in result.stdout
    assert "Dummy benchmark" in result.stdout
    assert "preset1, preset2" in result.stdout


def test_suite_run() -> None:
    result = runner.invoke(app, ["run", "Dummy benchmark suite"])
    assert result.exit_code == 0
    assert "RUN#1" in result.stdout
    assert "RUN#2" in result.stdout
    assert "preset1" in result.stdout
    assert "preset2" in result.stdout
