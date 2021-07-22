import unittest
from typer.testing import CliRunner
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from user_interfaces import cli

runner = CliRunner()


class TestArguments(unittest.TestCase):
    # def setUp(self):

    def invokeFactory(
        self, arr
    ):  # Function that invokes the method defined in the CLI app
        return runner.invoke(cli.app, arr)

    def test_helper(self):
        assert (
            self.invokeFactory(["--help"]).exit_code == 0
        )  # Tests main help command for CLI

    def test_listing(self):

        assert (
            self.invokeFactory(["list-benchmarks"]).exit_code == 0
        )  # Check if list-benchmark works fine

        assert (
            self.invokeFactory(["list-suites"]).exit_code == 0
        )  # Check if list-suite works fine

        assert (
            self.invokeFactory(["list-suites", "randomString"]).exit_code != 0
        )  # Check if list-suite gives error for random string appended

        assert (
            self.invokeFactory(["list-benchmarks", "randomString"]).exit_code != 0
        )  # Check if list-benchmark gives error for random string appended

    def test_run_benchmark(self):

        assert (
            "Error: Missing option" in self.invokeFactory(["run-benchmark"]).stdout
        )  # Check if no option flags given raises error

        assert (
            self.invokeFactory(
                ["run-benchmark", "-b", "dummy_benchmark", "-s", "settings1.json"]
            ).exit_code
            == 0
        )  # Check if correctly called run-benchmark exits sucessful

        assert (
            self.invokeFactory(
                [
                    "run-benchmark",
                    "-b",
                    "dummy_benchmark",
                    "-s",
                    "settings1.json",
                    "-v",
                    "3",
                ]
            ).exit_code
            == 0
        )  # Check if correctly called run-benchmark has verbosity intake exits sucessful

        assert (
            "implementation doesn't exist"
            in self.invokeFactory(["run-benchmark", "-b", "bad benchmark"]).stdout
        )  # Check if bad benchmark raise correct exception

        assert (
            self.invokeFactory(["run-benchmark", "--help"]).exit_code == 0
        )  # Check that help runs when invoked

    def test_run_suite(self):
        assert (
            "Error:" in self.invokeFactory(["run-suite"]).stdout
            and self.invokeFactory(["run-suite"]).exit_code != 0
        )  # Check if no option flags given raises error

        assert (
            self.invokeFactory(["run-suite", "example_suite.json"]).exit_code == 0
        )  # Checks if correctly called run-suite exits sucessfully

        assert (
            self.invokeFactory(["run-suite", "notAsuite.json"]).exit_code != 0
            and "implementation doesn't exist"
            in self.invokeFactory(["run-suite", "notAsuite.json"]).stdout
        )  # Check if bad benchmark raise correct exception

        assert (
            self.invokeFactory(["run-suite", "--help"]).exit_code == 0
        )  # Check that help runs when invoked

    def test_get_settings(self):
        assert (
            self.invokeFactory(
                ["get-settings", "blender_benchmark", "scenes", "list"]
            ).exit_code
            == 0
        )  # Check get_settings returns settings successful

        assert (
            self.invokeFactory(["get-settings", "noBenchmark", "noSettings"]).exit_code
            != 0
        )  # Check get settings exits unsuccessfully if wrong argument passed


if __name__ == "__main__":
    unittest.main()
