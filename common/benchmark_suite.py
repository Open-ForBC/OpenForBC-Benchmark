from .benchmark_wrapper import BenchmarkWrapper
from .benchmark_factory import BenchmarkFactory
import json
from .utils import checkSettings



class BenchmarkSuite(BenchmarkWrapper):
    def __init__(self, suite_info_path):
        suite_info_json = json.load(open(suite_info_path, "r"))
        self.name = checkSettings(suite_info_json, "name")
        self.description = checkSettings(suite_info_json, "description")
        self.benchmarkArray = []

        for bench in suite_info_json["benchmarks"]:
            self.benchmarkArray.append(
                BenchmarkFactory(
                    benchmark_name=bench["name"],
                    benchmark_settings_file=bench["settings"],
                )
            )

    def startBenchmark(self):
        self.counter = 0
        for b in self.benchmarkArray:
            b.startBenchmark()
            self.counter += 1

    def benchmarkStatus(self):
        return self.counter / len(self.benchmarkArray)


    def stopBenchmark():
        """Stops the benchmark"""
        pass

    def getSettings(self):

        pass

    def setSettings(self):
        pass
