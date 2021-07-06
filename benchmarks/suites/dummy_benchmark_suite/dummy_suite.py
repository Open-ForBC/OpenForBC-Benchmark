from ...common.benchmark_wrapper import BenchmarkWrapper
import pathlib
from ...dummy_classifier.implementation import DummyClassifier
from ...dummy_regressor.implementation import DummyRegressor
from ...common.benchmark_factory import BenchmarkFactory


class DummyBenchmarkSuite(BenchmarkWrapper):
    def __init__(self):
        self.settings = {}
        self.benchmarkArray = [DummyClassifier(), DummyRegressor()]
        self.bench_config = {}
        self.home_dir = pathlib.Path.cwd()

    def startBenchmark(self):
        for benchmark in self.benchmarkArray:
            burnin, rep = self.getSettings(benchmark)
            for _ in range(burnin + rep):
                print(benchmark.startBenchmark())

    def benchmarkStatus(self):
        # return self.processFinished/len(self.benchmarkArray)
        pass

    def stopBenchmark():
        """Stops the benchmark"""
        pass

    def getSettings(self, bmark):
        return bmark.getSettings()

    def setSettings():
        """Sets the benchmark settings according to the users choice"""
        pass
