import os
from pathlib import Path
import json
import subprocess
import sys
from prettytable import PrettyTable
from datetime import datetime

home_dir = Path.cwd()


def isBenchmark(path):
    """
    Checks to make sure given path belongs to a benchmark
    """
    try:
        if "benchmark_info.json" in os.listdir(path) and os.path.isdir(path):
            return True
    except NotADirectoryError or FileNotFoundError:
        return False
    return False


def getBenchmarksToRun():
    """
    Gets the Runnable benchmark while also performing the isBenchmark check
    """
    return [
        {"name": x}
        for x in os.listdir(os.path.join(home_dir, "benchmarks"))
        if isBenchmark(os.path.join(home_dir, "benchmarks", x))
    ]


def setItUp(benchmarkPath):
    """
    Executes the setup file if present in benchmark directory
    """
    if "setup.py" in os.listdir(benchmarkPath):
        try:
            process = subprocess.run(
                [sys.executable, os.path.join(benchmarkPath, "setup.py")],
                check=True,
                universal_newlines=True,
            )
        except subprocess.CalledProcessError as e:
            print(e.output)
        if process.returncode != 0:
            raise process.stderr
    elif "setup.sh" in os.listdir(benchmarkPath):
        pass  # TODO: call setup.sh from here
    else:
        raise Exception(
            "Setup file extension not supported please use a .py file or bash script."
        )


def getSuitesToRun():
    """
    Gets all the runnable suites
    """
    return [{"name": x} for x in os.listdir(os.path.join(home_dir, "suites"))]


def getSettings(bmark, runType):
    """
    Gets a list of available settings
    """
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


def suiteMaker(suiteBuild: dict, suiteList: list):
    """
    Builds up a suite according to given details
    """
    runnerDict = dict(
        {
            "name": suiteBuild["SuiteName"],
            "description": suiteBuild["SuiteDescription"],
            "benchmarks": suiteList,
        }
    )
    suitePath = os.path.join(home_dir, "suites", suiteBuild["FileName"] + ".json")
    with open(suitePath, "w") as configFile:
        json.dump(runnerDict, configFile, indent=4)


def logIT(benchmark, logs, settings=None, pathToLog="./logs"):
    """
    Logs the given list/dictionary
    """
    if logs is None:
        logs = "The Benchmark doesn't return any log"
    [date, time] = str(datetime.now()).split(" ")
    date = "".join(str(date).split("-"))
    time = "".join(str(time).split(":"))[:-7]
    if settings is not None:
        path = Path.cwd().joinpath(
            pathToLog, benchmark, str(settings)[:-5], str(date) + "_" + str(time)
        )
    else:
        path = Path.cwd().joinpath(pathToLog, benchmark, str(date) + "_" + str(time))
    path.mkdir(parents=True, exist_ok=True)
    with open(os.path.join(path, "output.log"), "a") as logFile:
        logFile.write(logs if isinstance(logs, str) else json.dumps(logs, indent=4))


def tablify(legend, data, sorting=False, col=0):
    """
    Creates a pretty table out of data provided
    """
    table = PrettyTable(legend)
    if sorting:
        data.sort(key=lambda x: x[col])
    for rec in data:
        table.add_row(rec)
    return table
