<<<<<<< HEAD
<<<<<<< HEAD
import json
from .benchmark_wrapper import BenchmarkWrapper
from .benchmark_factory import BenchmarkFactory

class BenchmarkSuite(BenchmarkWrapper):
    def __init__(self, suite_info_path):
        suite_info_json = json.load(open(suite_info_path, "r"))
        self.name = suite_info_json["name"]
        self.description = suite_info_json["description"]
        self.benchmarkArray = []

        for bench in suite_info_json["benchmarks"]:
            self.benchmarkArray.append(
                BenchmarkFactory(
                    benchmark_name=bench["name"],
                    benchmark_settings_file=bench["settings"],
                )
            )
=======
=======
import sys
import os
sys.path.append(os.path.dirname(__file__))

>>>>>>> 24ad128... Additional examples
from benchmark_wrapper import BenchmarkWrapper
from benchmark_factory import BenchmarkFactory
import pathlib
import json
import os


class BenchmarkSuite(BenchmarkWrapper):
    def __init__(self, suite_info_path):
        suite_info_json = json.load(open(suite_info_path, 'r'))
        self.name = suite_info_json['name']
        self.description = suite_info_json['description']
        self.benchmarkArray = []

        for bench in suite_info_json['benchmarks']:
            self.benchmarkArray.append(BenchmarkFactory(benchmark_name=bench['name'], benchmark_settings_file=bench['settings']))
>>>>>>> c0b38b3... Cleaning up...

    def startBenchmark(self):
        for b in self.benchmarkArray:
            b.startBenchmark()

    def benchmarkStatus():
        """Fetches the status of the current benchmark"""
        pass

    def stopBenchmark():
        """Stops the benchmark"""
        pass

    def getSettings(self, bmark):
        pass

    def setSettings(self):
        pass
<<<<<<< HEAD
<<<<<<< HEAD
=======

if __name__=="__main__":
    BenchmarkSuite("/Users/gabrielegaetanofronze/gitstuff/OpenForBC-Benchmark/common/suite_info.json").startBenchmark()
>>>>>>> c0b38b3... Cleaning up...
=======
>>>>>>> 24ad128... Additional examples
