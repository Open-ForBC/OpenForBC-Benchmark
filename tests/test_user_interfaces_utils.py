import unittest
import sys
import os
from pathlib import Path
import json
from datetime import datetime
import shutil

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from user_interfaces.utils import (  # noqa: E402
    getSettings,
    getSuitesToRun,
    getBenchmarksToRun,
    setItUp,
    suiteMaker,
    logIT,
    tablify,
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


class TestLogging(unittest.TestCase):
    def setUp(self):
        logIT(
            benchmark="MyBenchmark",
            logs="hello world",
            settings="settings1.json",
            pathToLog=os.path.join("logs", "temp-log"),
        )

    def tearDown(self):
        shutil.rmtree(os.path.join(Path.cwd(), "logs", "temp-log"))

    def test_logging(self):
        my_logs = "hello world"
        gotten_logs = ""
        [date, time] = str(datetime.now()).split(" ")
        date = "".join(str(date).split("-"))
        time = "".join(str(time).split(":"))[:-7]
        path = Path.cwd().joinpath(
            "logs", "temp-log", "MyBenchmark", "settings1", str(date)
            + "_" + str(time)
        )
        with open(os.path.join(path, "output.log"), "r") as logFile:
            gotten_logs = logFile.read()
        gotten_log = gotten_logs.strip('"')
        self.assertEqual(my_logs, gotten_log)


class TestTableMaker(unittest.TestCase):
    def test_tablify(self):
        input_data = [[1, 2, 3], [4, 5, 6]]
        gotten_output = str(tablify(
            legend=["a", "b", "c"], data=input_data, sorting=True
        ))
        my_table = "+---+---+---+\n| a | b | c |\n+---+---+---+\n| 1 | 2 | 3 |\n| 4 | 5 | 6 |\n+---+---+---+"
        self.assertEqual(my_table, gotten_output)


if __name__ == "__main__":
    unittest.main()
