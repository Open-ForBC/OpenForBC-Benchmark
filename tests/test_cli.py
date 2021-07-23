import unittest
from typer.testing import CliRunner
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from user_interfaces import cli

runner = CliRunner()


class TestArguments(unittest.TestCase):
    def invokeFactory(
        self, arr
    ):  # Function that invokes the method defined in the CLI app
        return runner.invoke(cli.app, arr)

    def test_helper(self):
        self.assertEqual(
            self.invokeFactory(["--help"]).exit_code, 0
        )  # Tests main help command for CLI

    def test_listing(self):

        self.assertEqual(
            self.invokeFactory(["list-benchmarks"]).exit_code, 0
        )  # Check: list-benchmark works fine

        self.assertEqual(
            self.invokeFactory(["list-suites"]).exit_code, 0
        )  # Check: list-suite works fine

        self.assertNotEqual(
            self.invokeFactory(["list-suites", "randomString"]).exit_code, 0
        )  # Check: list-suite gives error for random string appended

        self.assertNotEqual(
            self.invokeFactory(["list-benchmarks", "randomString"]).exit_code, 0
        )  # Check: list-benchmark gives error for random string appended

    def test_run_benchmark(self):
        self.assertTrue(
            "Error: Missing option" in self.invokeFactory(["run-benchmark"]).stdout
        )  # Check: no option flags given raises error

        self.assertEqual(
            self.invokeFactory(
                ["run-benchmark", "-b", "dummy_benchmark", "-s", "settings1.json"]
            ).exit_code,
            0,
        )  # Check: correctly called run-benchmark exits sucessful

        self.assertEqual(
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
            ).exit_code,
            0,
        )  # Check: correctly called run-benchmark has verbosity intake exits sucessful

        self.assertTrue(
            "implementation doesn't exist"
            in self.invokeFactory(["run-benchmark", "-b", "bad benchmark"]).stdout
        )  # Check: bad benchmark raise correct exception

        self.assertEqual(
            self.invokeFactory(["run-benchmark", "--help"]).exit_code, 0
        )  # Check: help runs when invoked

    def test_run_suite(self):
        self.assertTrue("Error:" in self.invokeFactory(["run-suite"]).stdout)
        self.assertNotEqual(
            self.invokeFactory(["run-suite"]).exit_code, 0
        )  # Check: no option flags given raises error

        self.assertEqual(
            self.invokeFactory(["run-suite", "example_suite.json"]).exit_code, 0
        )  # Checks: correctly called run-suite exits sucessfully

        self.assertNotEqual(
            self.invokeFactory(["run-suite", "notAsuite.json"]).exit_code, 0
        )  # Check: bad suite name doesn't exit successfully

        self.assertTrue(
            "implementation doesn't exist"
            in self.invokeFactory(["run-suite", "notAsuite.json"]).stdout
        )  # Check: bad benchmark raise correct exception
        self.assertEqual(
            self.invokeFactory(["run-suite", "--help"]).exit_code, 0
        )  # Check: help runs when invoked

    def test_get_settings(self):
        self.assertEqual(
            self.invokeFactory(
                ["get-settings", "blender_benchmark", "scenes", "list"]
            ).exit_code,
            0,
        )  # Check: get_settings returns settings successful

        self.assertNotEqual(
            self.invokeFactory(["get-settings", "noBenchmark", "noSettings"]).exit_code,
            0,
        )  # Check: get settings exits unsuccessfully if wrong argument passed


if __name__ == "__main__":
    unittest.main()
