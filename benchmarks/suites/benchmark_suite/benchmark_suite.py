from ...common.benchmark_wrapper import BenchmarkWrapper
from ...common.benchmark_factory import BenchmarkFactory
import pathlib
import json
import os


class BenchmarkSuite(BenchmarkWrapper):
    def __init__(self):
        self.settings = {}
        self.preset = {}
        self.benchmarkArray = []
        self.bench_config = {}
        self.home_dir = pathlib.Path.cwd()

    def startBenchmark(self):
        self.setSettings()
        for runnable in self.bench_config:
            _bmarkObj = BenchmarkFactory().getBenchmarkModule(
                file_path=os.path.join("benchmarks", runnable["name"])
            )
            print(_bmarkObj().startBenchmark())
        pass

    def benchmarkStatus():
        """Fetches the status of the current benchmark"""
        pass

    def stopBenchmark():
        """Stops the benchmark"""
        pass

    def getSettings():
        """Gets the benchmark settings according to the users choice"""
        pass

    def setSettings(self):
        with open(
            pathlib.Path.cwd().joinpath(
                "benchmarks", "benchmark_suite", "suite_info.json"
            )
        ) as config:
            self.bench_config = json.load(config)["benchmarks"]
