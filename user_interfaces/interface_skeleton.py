from common.benchmark_factory import BenchmarkFactory
from common.benchmark_wrapper import BenchmarkWrapper
from common.benchmark_suite import BenchmarkSuite


class InterfaceSkeleton(BenchmarkWrapper):
    def __init__(self):
        pass

    def startBenchmark(
        self,
        runType="benchmark",
        bmark=None,
        settings=None,
        suitePath=None,
        verbosity=None,
    ):
        if runType.lower() == "benchmark":
            benchmarkObject = BenchmarkFactory(benchmark_name=bmark, benchmark_settings_file=settings)
            benchmarkObject.setSettings(settings)
            return benchmarkObject.startBenchmark(verbosity)
        elif runType.lower() == "suite":
            return BenchmarkSuite(suite_info_path=suitePath).startBenchmark()

    def benchmarkStatus():
        """Fetches the status of the current benchmark"""
        pass

    def stopBenchmark():
        """Stops the benchmark"""
        pass

    def getSettings(self, bmark):
        return BenchmarkFactory(
            benchmark_name=bmark
        ).getSettings()
        pass

    def setSettings(self):
        pass
