from common.benchmark_wrapper import BenchmarkWrapper
import json


class DummyBenchmark(BenchmarkWrapper):

    """
    This is a dummy benchmark class to demonstrate how to construct code for benchmark implementation.
    """

    def __init__(self):
        self.to_print = "Ciao"
        pass

    def setSettings(self, settings_file):
        self.to_print = json.load(open(settings_file, "r"))["to_print"]
        pass

    def startBenchmark(self,verbosity = None):
        print(self.to_print)
        return

    def benchmarkStatus():
        pass

    def getSettings(self):
        pass

    def stopBenchmark():
        pass
