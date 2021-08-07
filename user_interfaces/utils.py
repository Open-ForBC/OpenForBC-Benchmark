import os
from pathlib import Path
import json
import subprocess
import sys
from prettytable import PrettyTable
from datetime import datetime

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
        try:                                                                                                                                                            
            process = subprocess.run(
                [sys.executable, os.path.join(benchmarkPath, "setup.py")], check=True, universal_newlines=True
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


def suiteMaker(suiteBuild:dict,suiteList:list):
    runnerDict = dict(
        {
            "name": suiteBuild["SuiteName"],
            "description": suiteBuild["SuiteDescription"],
            "benchmarks": suiteList,
        }
    )
    suitePath = os.path.join(
        home_dir, "suites", suiteBuild["FileName"] + ".json"
    )
    with open(suitePath, "w") as configFile:
        json.dump(runnerDict, configFile, indent=4)

def logIT(benchmark,logs,settings = None,pathToLog = "./logs"):
    if logs is None:
        logs = "The Benchmark doesn't return any log"
    if settings != None:
        path = Path.cwd().joinpath(pathToLog,benchmark,str(settings)[:-5],str(datetime.now())[:-8])
    else:
        path = Path.cwd().joinpath(pathToLog,benchmark,str(datetime.now())[:-7])
    path.mkdir(parents=True, exist_ok=True)
    with open(os.path.join(path,'output.log'), "a") as logFile:
        logFile.write(json.dumps(logs, indent=4))


def tablify(legend,data,sorting = False,col = 0):
    table = PrettyTable(legend)
    if sorting:
        data.sort(key = lambda x: x[col])
    for rec in data:
        table.add_row(rec)
    return table