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

    def getBenchmarksToRun(self,omitters):
        return [{'name': x} for x in os.listdir(os.path.join(self.home_dir,'../benchmarks')) if x.find(omitters[0]) == -1 and x.find(omitters[1]) == -1]       #TODO: make a more robust check and not O(n^2)

    def runner(self):
        nr = []
        omitters = ['_suite','common']
        runnables = self.getBenchmarksToRun(omitters)
        benchmarks = [
            {
                "type": "checkbox",
                "message": "Select Benchmark",
                "name": "benchmark",
                "choices": runnables,
                'validate': lambda answer: ValueError('no input') if len(answer) == 0 else True
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
                    "filter": lambda val: float(val)
                }
            ]
            gpuUsage = prompt(gpuUsage)
            self.runnerDict[bmark] = gpuUsage["gpuUsage"]
        with open(f"{self.home_dir+'/../benchmarks/benchmark_suite/benchmark_info.json'}", "w") as configFile:
            json.dump(self.runnerDict, configFile)


if __name__ == "__main__":
    UserMenu().runner()
