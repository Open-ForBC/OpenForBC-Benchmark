from __future__ import print_function, unicode_literals
from pprint import pprint
from PyInquirer import prompt
import json
import os


class UserMenu:
    def __init__(self):
        self.selectBenchmark: dict
        self.gpuUsage: float
        self.home_dir = os.path.dirname(os.path.abspath(__file__))
        self.runnerDict: dict = {}

    def runner(self):
        benchmarks = [
            {
                "type": "checkbox",
                "message": "Select Benchmark",
                "name": "benchmark",
                "choices": [
                    {"name": "MLPerf"},
                    {"name": "3D Mark"},
                    {"name": "Unigine Heaven"},
                    {"name": "Dummy Benchmark"},
                ],
                "validate": lambda answer: "You must choose at least one Benchmark to run."
                if len(answer) == 0
                else True,
            }
        ]
        self.selectBenchmark = prompt(benchmarks)
        pprint(self.selectBenchmark)
        for bmark in self.selectBenchmark["benchmark"]:
            gpuUsage = [
                {
                    "type": "input",
                    "name": "gpuUsage",
                    "message": f"Assigned GPU usage for {bmark}?(0-1)",
                    "validate": lambda val: float(val) > 0.0 and float(val) <= 1.0,
                }
            ]
            gpuUsage = prompt(gpuUsage)
            self.runnerDict[bmark] = gpuUsage["gpuUsage"]
        with open(f"{self.home_dir}/../config/benchmarkconfig.json", "w") as configFile:
            json.dump(self.runnerDict, configFile)


if __name__ == "__main__":
    UserMenu().runner()
