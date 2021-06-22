from benchmark_wrapper import BenchmarkWrapper
from benchmark_wrapper import DummyBenchmark
from dummy import DummyClassifier, DummyRegressor


class BenchmarkSuite:
    benchmarkArray:BenchmarkWrapper

    def __init__(self):
        self.settings = {}
        self.preset = {}

    def startBenchmark(self):
        dumClf = DummyClassifier(self.settings["Dummy"], self.preset["Dummy"])
        dumReg = DummyRegressor()
        result = {"classifier":dumClf.dummyClf(),
                  "regressor":dumReg.dummyReg()}
        return result

    def benchmarkStatus():
        pass
    
    def stopBenchmark():
        pass

    def getBenchmarkConfig(self):
        dummy = DummyBenchmark(None)
        self.settings["Dummy"] = dummy.getSettings()
        self.preset["Dummy"] = dummy.getPresets()

