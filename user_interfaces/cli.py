from __future__ import print_function, unicode_literals
from math import fabs
from operator import truediv
from PyInquirer import prompt
import json
import os
from utils import isBenchmark
import pathlib
# import typer
import sys
from benchmarks.benchmark_suite.implementation import BenchmarkSuite


class UserMenu:
    def __init__(self):
        self.selectBenchmark: dict
        self.gpuUsage: float
        self.home_dir = pathlib.Path.cwd()
        self.runnerDict: dict = {}

    def getBenchmarksToRun(self):
        return [
            {"name": x}
            for x in os.listdir(os.path.join(self.home_dir, "benchmarks"))
            if isBenchmark(os.path.join(self.home_dir, "benchmarks", x)) == True
        ]

    def runner(self):
        runnables = self.getBenchmarksToRun()
        benchmarks = [
            {
                "type": "checkbox",
                "message": "Select Benchmark",
                "name": "benchmark",
                "choices": runnables,
                "validate": lambda answer: ValueError("no input")
                if len(answer) == 0
                else True,
            }
        ]
        self.selectBenchmark = prompt(benchmarks)
        for bmark in self.selectBenchmark["benchmark"]:
            gpuUsage = [
                {
                    "type": "input",
                    "name": "gpuUsage",
                    "message": f"Assigned GPU usage for {bmark}?(0-1)",
                    "validate": lambda val: float(val) > 0.0 and float(val) <= 1.0,
                    "filter": lambda val: float(val),
                }
            ]
            gpuUsage = prompt(gpuUsage)
            self.runnerDict[bmark] = gpuUsage["gpuUsage"]
        with open(
            self.home_dir.joinpath("benchmarks", "benchmark_suite", "suite_info.json"),
            "w",
        ) as configFile:
            json.dump(self.runnerDict, configFile)


if __name__ == "__main__":
    UserMenu().runner()
    BenchmarkSuite().startBenchmark()



