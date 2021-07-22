import json
from .benchmark_wrapper import BenchmarkWrapper
from .benchmark_factory import BenchmarkFactory


class BenchmarkSuite(BenchmarkWrapper):
    """
    Given suite path, the class appends given benchmark
    object(Given by BenchmarkFactory) to benchmark array.
    """

    def __init__(self, suite_info_path):
        with open(suite_info_path, "r") as s:
            try:
                suite_info_json = json.load(s)
            except FileNotFoundError as e:
                raise Exception(f"{e}: Suites info json doesn't exist.")

        self.name = suite_info_json["name"]
        self.description = suite_info_json["description"]
        self.benchmarkArray = []
        for bench in suite_info_json["benchmarks"]:
            try:
                self.benchmarkArray.append(
                    BenchmarkFactory(
                        benchmark_name=bench["name"],
                        benchmark_settings_file=bench["settings"],
                    )
                )
            except:
                raise Exception("Benchmark Appending didn't finish")

    def startBenchmark(self):
        for b in self.benchmarkArray:
            try:
                b.startBenchmark()
            except:
                raise Exception("Benchmark Suite couldn't start a benchmark")

    def benchmarkStatus():
        """Fetches the status of the current benchmark"""
        raise Exception("Function not defined")

    def stopBenchmark():
        """Stops the benchmark"""
        raise Exception("Function not defined")

    def getSettings(self, bmark):
        raise Exception("Function not defined")

    def setSettings(self):
        raise Exception("Function not defined")
