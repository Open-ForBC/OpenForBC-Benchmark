import unittest
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from user_interfaces.utils import (
    getSettings,
    getSuitesToRun,
    isBenchmark,
    getBenchmarksToRun,
    setItUp,
)


class TestVerificationFunctions(unittest.TestCase):
    def test_isBenchmark(self):
        bmark_list = os.listdir(os.path.join(Path.cwd(), "benchmarks"))
        for bmark in bmark_list:
            self.assertTrue(isBenchmark(os.path.join(Path.cwd(), "benchmarks", bmark)))


class TestListingFunctions(unittest.TestCase):
    def test_get_benchmark(self):
        bmark_list = os.listdir(os.path.join(Path.cwd(), "benchmarks"))
        bmarks = getBenchmarksToRun()
        self.assertEqual([bmarks[0].values()].sort(), bmark_list.sort())

    def test_get_suite(self):
        suites_list = os.listdir(os.path.join(Path.cwd(), "suites"))
        suites = getSuitesToRun()
        self.assertEqual([suites[0].values()].sort(), suites_list.sort())

    def test_get_settings(self):
        settings_list = os.listdir(
            Path.cwd().joinpath("benchmarks", "dummy_benchmark", "settings")
        )
        settings = getSettings("dummy_benchmark", "benchmark")
        self.assertEqual([settings[0].values()].sort(), settings_list.sort())


class TestSetup(unittest.TestCase):
    def setUp(self) -> None:
        with open(Path.cwd().joinpath("setup.py"), "x") as setupFile:
            setupFile.write("""print("Setup Sucessful!")""")

    def tearDown(self) -> None:
        os.remove(Path.cwd().joinpath("setup.py"))

    def test_setup(self):
        setItUp(Path.cwd())


if __name__ == "__main__":
    unittest.main()
