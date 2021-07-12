from common.benchmark_factory import BenchmarkFactory
from common.benchmark_wrapper import BenchmarkWrapper


class InterfaceSkeleton(BenchmarkWrapper):
    def __init__(self):
        pass

    def startBenchmark(self, bmark, settings):
        BenchmarkFactory(
            benchmark_name=bmark, benchmark_settings_file=settings
        ).startBenchmark()

    def benchmarkStatus():
        """Fetches the status of the current benchmark"""
        pass

    def stopBenchmark():
        """Stops the benchmark"""
        pass

    def getSettings(self, bmark, settings, command):
        BenchmarkFactory(
            benchmark_name=bmark, benchmark_settings_file=settings
        ).getSettings(command)
        pass

    def setSettings(self):
        pass
