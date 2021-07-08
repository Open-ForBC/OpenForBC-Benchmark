import os
from pathlib import Path
import json

home_dir = Path.cwd()


def isBenchmark(path):
    try:
        if "benchmark_info.json" in os.listdir(path) and os.path.isdir(path):
            return True
    except NotADirectoryError or FileNotFoundError:
        return False
    return False


def getBenchmarksToRun():
    return [
        {"name": x}
        for x in os.listdir(os.path.join(home_dir, "benchmarks"))
        if isBenchmark(os.path.join(home_dir, "benchmarks", x))
    ]

def getSuitesToRun():
    return [
        {"name": x}
        for x in os.listdir(os.path.join(home_dir, "benchmarks","suites"))
    ]

def getSettings(bmark,runType):
    if runType == 'Suite':
        return [
            dict({"name": x})
            for x in os.listdir(home_dir.joinpath("benchmarks","suites" , bmark, "settings"))
        ]
    else:
        return [
            dict({"name": x})
            for x in os.listdir(home_dir.joinpath("benchmarks", bmark, "settings"))
        ]


def setSettings(runnerDict):
    with open(
        
        home_dir.joinpath("benchmarks", "benchmark_suite", "settings", "settings1.json"),
        "w",
    ) as configFile:
        json.dump(runnerDict, configFile, indent=4)


class EmptyBenchmarkList(BaseException):
    def __str__(self):
        return "Please select benchmark(s) to run by pressing spacebar to select."
