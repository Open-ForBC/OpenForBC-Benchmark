import os
from pathlib import Path
import json
import subprocess
import sys


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


def setItUp(benchmarkPath):
    if "setup.py" in os.listdir(benchmarkPath):
        setUp = subprocess.Popen(
            [sys.executable, os.path.join(benchmarkPath, "setup.py")],
            stdin=subprocess.PIPE,
        )
    elif "setup.sh" in os.listdir(benchmarkPath):
        pass  # TODO: call setup.sh from here
    else:
        raise Exception(
            "Setup file extension not supported please use a .py file or bash script."
        )


def getSuitesToRun():
    return [{"name": x} for x in os.listdir(os.path.join(home_dir, "suites"))]


def getSettings(bmark, runType):
    if runType == "Suite":
        return [
            dict({"name": x})
            for x in os.listdir(
                home_dir.joinpath("benchmarks", "suites", bmark, "settings")
            )
        ]
    else:
        return [
            dict({"name": x})
            for x in os.listdir(home_dir.joinpath("benchmarks", bmark, "settings"))
        ]


class EmptyBenchmarkList(BaseException):
    def __str__(self):
        return "Please select benchmark(s) to run by pressing spacebar to select."
