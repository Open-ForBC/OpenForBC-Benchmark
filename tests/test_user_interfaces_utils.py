import unittest
import sys
import os
from pathlib import Path
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from user_interfaces.utils import ( # noqa: E402
    getSettings,
    getSuitesToRun,
    getBenchmarksToRun,
    setItUp,
    suiteMaker,
)


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


class TestSuiteMaker(unittest.TestCase):
    def setUp(self) -> None:
        self._suiteDict = {
            "SuiteName": "testsuite",
            "SuiteDescription": "Test Description",
            "FileName": "testfile",
        }
        self._suiteList = [
            dict({"name": "dummy_benchmark", "settings": "settings1.json"}),
            dict({"name": "dummy_benchmark", "settings": "settings2.json"}),
        ]
        self.expectedOutput = {
            "name": "testsuite",
            "description": "Test Description",
            "benchmarks": [
                {"name": "dummy_benchmark", "settings": "settings1.json"},
                {"name": "dummy_benchmark", "settings": "settings2.json"},
            ],
        }

    def tearDown(self) -> None:
        os.remove(os.path.join(Path.cwd(), "suites", "testfile.json"))

    def test_suite_maker(self):
        suiteMaker(self._suiteDict, self._suiteList)
        suitePath = os.path.join(Path.cwd(), "suites", "testfile.json")
        with open(suitePath, "r") as f:
            output = json.load(f)
        self.assertEqual(self.expectedOutput, output)


if __name__ == "__main__":
    unittest.main()
