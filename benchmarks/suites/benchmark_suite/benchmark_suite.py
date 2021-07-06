from ...common.benchmark_wrapper import BenchmarkWrapper
from ...common.benchmark_factory import BenchmarkFactory
import pathlib
import json
import os


class BenchmarkSuite(BenchmarkWrapper):
    def __init__(self):
        self.settings = {}
        self.bench_config = {}
        self.benchmarkArray = []
        self.home_dir = pathlib.Path.cwd()
        self.settings_loc = self.home_dir.joinpath(
            "benchmarks", "benchmark_suite", "suite_info.json"
        )

    def startBenchmark(self):
        self.setSettings()
        for benchmark in self.benchmarkArray:
            burnin, rep = self.getSettings(benchmark)
            for _ in range(burnin + rep):
                print(benchmark.startBenchmark())

    def benchmarkStatus():
        """Fetches the status of the current benchmark"""
        pass

    def stopBenchmark():
        """Stops the benchmark"""
        pass

    def getSettings(self, bmark):
        return bmark.getSettings()

    def setSettings(self):
        with open(self.settings_loc) as config:
            self.bench_config = json.load(config)["benchmarks"]
        for runnable in self.bench_config:
            _bmarkObj = BenchmarkFactory().getBenchmarkModule(
                file_path=os.path.join("benchmarks", runnable["name"])
            )
            self.benchmarkArray.append(_bmarkObj())
