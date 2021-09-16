from common.benchmark_wrapper import BenchmarkWrapper
import json
import os


class DummyBenchmark(BenchmarkWrapper):

    """
    This is a dummy benchmark class to demonstrate how to construct code for benchmark implementation.
    """

    def __init__(self):
        self.to_print = "Ciao"
        pass

    def setSettings(self, settings_file):
        settings = os.path.join(os.path.dirname(__file__), "settings", settings_file)
        self.to_print = json.load(open(settings, "r"))["to_print"]

    def startBenchmark(self, verbosity=None):
        print(self.to_print)
        return {"output": self.to_print}

    def benchmarkStatus():
        pass

    def getSettings(self):
        pass

    def stopBenchmark():
        pass
