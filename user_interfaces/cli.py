from __future__ import print_function, unicode_literals
from PyInquirer import prompt
import json
import os
from user_interfaces.utils import isBenchmark
import pathlib
import typer
from .interface_skeleton import InterfaceSkeleton
from .utils import EmptyBenchmarkList

app = typer.Typer()


class UserMenu:
    def __init__(self):
        self.selectBenchmark: dict = {}
        self.gpuUsage: float
        self.home_dir = pathlib.Path.cwd()
        self.runnerDict: dict = {}
        self.benchmarks = [
            {
                "type": "checkbox",
                "message": "Select Benchmark",
                "name": "benchmark",
                "qmark": "💻",
                "choices": self.getBenchmarksToRun(),
                "validate": lambda answer: ValueError("no input")
                if len(answer) == 0
                else True,
            }
        ]

    def getBenchmarksToRun(self):
        return [
            {"name": x}
            for x in os.listdir(os.path.join(self.home_dir, "benchmarks"))
            if isBenchmark(os.path.join(self.home_dir, "benchmarks", x)) == True
        ]

    def runner(self):
        self.benchmarkBanner()
        for bmark in self.selectBenchmark["benchmark"]:
            self.gpuUsage = [
                {
                    "type": "input",
                    "name": "gpuUsage",
                    "qmark": "➡️",
                    "message": f"Assigned GPU usage for {bmark}?(0-1)",
                    "validate": lambda val: float(val) > 0.0 and float(val) <= 1.0,
                    "filter": lambda val: float(val),
                }
            ]
            gpuUsage = prompt(self.gpuUsage)
            self.runnerDict[bmark] = gpuUsage["gpuUsage"]
        with open(
            self.home_dir.joinpath("benchmarks", "benchmark_suite", "suite_info.json"),
            "w",
        ) as configFile:
            json.dump(self.runnerDict, configFile)
        InterfaceSkeleton().startBenchmark()

    def benchmarkBanner(self):
        print("   ___                   _____          ____   ____ ")
        print("  / _ \ _ __   ___ _ __ |  ___|__  _ __| __ ) / ___|")
        print(" | | | | '_ \ / _ \ '_ \| |_ / _ \| '__|  _ \| |    ")
        print(" | |_| | |_) |  __/ | | |  _| (_) | |  | |_) | |___ ")
        print("  \___/| .__/ \___|_| |_|_|  \___/|_|  |____/ \____|")
        print("       |_|                                          ")
        print(" ====Welcome to the OpenForBC Benchmarking Tool====")
        self.selectBenchmark = prompt(self.benchmarks)
        if not self.selectBenchmark["benchmark"]:
            raise EmptyBenchmarkList


# if __name__ == "__main__":
#     UserMenu().runner()
#     BenchmarkSuite().startBenchmark()
