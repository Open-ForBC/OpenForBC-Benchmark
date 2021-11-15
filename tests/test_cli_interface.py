import unittest
from typer.testing import CliRunner
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from user_interfaces import cli # noqa: E402

runner = CliRunner()


class HelperFunction:
    def invokeFactory(argv):# Function that invokes the method defined in the CLI app
        return runner.invoke(cli.app, argv)


class RunBenchmark(unittest.TestCase):
    def test_benchmark_runner(self):
        self.assertEqual(
            HelperFunction.invokeFactory(
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

    def test_suite_runner(self):
        self.assertEqual(
            HelperFunction.invokeFactory(
                [
                    "run-suite",
                    "example_suite.json"]).exit_code, 0
        )  # Checks: correctly called run-suite exits sucessfully


if __name__ == "__main__":
    unittest.main()
