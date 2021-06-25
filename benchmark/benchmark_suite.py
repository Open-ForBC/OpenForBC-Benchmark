from benchmark_wrapper import BenchmarkWrapper
import json
from collections import deque
from dummy_classifier import DummyClassifier
from dummy_regressor import DummyRegressor

class BenchmarkSuite:
    def __init__(self):
        self.settings = {}
        self.preset = {}
        self.benchmarkArray: BenchmarkWrapper = []
        self.bench_config = {}

    def startBenchmark(self):
        for bname, gpuUsage in self.bench_config.items():
            if bname.lower() == "mlperf":
                pass
            if bname.lower() == "dummy benchmark":
                self.benchmarkArray.append(DummyClassifier(gpuUsage))
                self.benchmarkArray.append(DummyRegressor(gpuUsage = gpuUsage))
        for obj in self.benchmarkArray:
            print(type(obj))
            print(obj.benchmarkName, obj.gpuUsage)

    def benchmarkStatus():
        pass

    def stopBenchmark():
        pass

    def getBenchmarkConfig(self):
        with open("../config/benchmarkconfig.json") as f:
            self.bench_config = json.load(f)


if __name__ == "__main__":
    ins = BenchmarkSuite()
    ins.getBenchmarkConfig()
    ins.startBenchmark()
