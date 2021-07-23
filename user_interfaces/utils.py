import os
from pathlib import Path
import json
import subprocess
import sys
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

class EmptyBenchmarkList(BaseException):
    def __str__(self):
        return "Please select benchmark(s) to run by pressing spacebar to select."

# def logIT(benchmark,settings,logs,pathToLog = "/var/log/openforbc"):
#     path = Path(pathToLog).joinpath(benchmark,str(settings)[:-5],str(datetime.now())[:-8],'output.log')
#     path.mkdir(parents=True, exist_ok=True)
#     with open(path, "w") as logFile:
#             logFile.writelines(logs)

#TODO: fix the error given by logIT due to permissions
# var/log/openforbc/[benchmark name]/[preset name]/[date]/[output files]