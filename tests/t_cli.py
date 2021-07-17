import pytest
from typer.testing import CliRunner
# from click.testing import CliRunner
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from user_interfaces import cli

runner = CliRunner()

def test_assertionError():
    with pytest.raises(AssertionError):
        runner.invoke(cli.interactive("hello world"))
        # print(cli.interactive("hello world"))
        runner.invoke(cli.interactive([1,2,3,4]))
        runner.invoke(cli.interactive({"a":"dc"}))
    # assert isinstance(res.exception, exceptions.Exit)

def test_get_settings():
    with pytest.raises(Exception):
        a = runner.invoke(cli.get_settings(benchmark="Lala",command = "Doesn't exist"))
    