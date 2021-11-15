import json
import os
from pathlib import Path
from user_interfaces.utils import setItUp
from .benchmark_wrapper import BenchmarkWrapper
from .benchmark_factory import BenchmarkFactory


class BenchmarkSuite(BenchmarkWrapper):
    def __init__(self, suite_info_path):
        suite_info_json = json.load(open(suite_info_path, "r"))
        self.name = suite_info_json["name"]
        self.description = suite_info_json["description"]
        self.benchmarkArray = []
        self.output = []

        for bench in suite_info_json["benchmarks"]:
            benchmarkPath = os.path.join(Path.cwd(), "benchmarks", bench["name"])
            if (
                Path(os.path.join(benchmarkPath, "setup.py")).exists()
                or Path(os.path.join(benchmarkPath, "setup.sh")).exists()
            ):
                setItUp(benchmarkPath)
            self.benchmarkArray.append(
                (BenchmarkFactory(
                    benchmark_name=bench["name"],
                    benchmark_settings_file=bench["settings"],
                ), bench["settings"])
            )

    def startBenchmark(self):
        for benchmarks, settings in self.benchmarkArray:
            self.setSettings(benchmarks, settings)
            self.output.append(benchmarks.startBenchmark())
        return self.output

    def benchmarkStatus():
        """Fetches the status of the current benchmark"""
        pass

    def stopBenchmark():
        """Stops the benchmark"""
        pass

    def getSettings(self):
        pass

    def setSettings(self, benchmarkObject, settings):
        benchmarkObject.setSettings(settings)
