from ...common.benchmark_wrapper import BenchmarkWrapper
import pathlib
from ...dummy_classifier.implementation import DummyClassifier
from ...dummy_regressor.implementation import DummyRegressor


class DummyBenchmarkSuite(BenchmarkWrapper):
    def __init__(self):
        self.settings = {}
        self.preset = {}
        self.benchmarkArray = []
        self.bench_config = {}
        self.home_dir = pathlib.Path.cwd()
        self.benchs = [DummyClassifier(), DummyRegressor()]

    def startBenchmark(self):
        for bmarks in self.benchs:
            print(bmarks.startBenchmark())
        pass

    def benchmarkStatus(self):
        # return self.processFinished/len(self.benchmarkArray)
        pass

    def stopBenchmark():
        """Stops the benchmark"""
        pass

    def getSettings():
        """Gets the benchmark settings according to the users choice"""
        pass

    def setSettings():
        """Sets the benchmark settings according to the users choice"""
        pass
