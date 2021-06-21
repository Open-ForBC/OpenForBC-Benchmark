from typing import Optional
from dummy import DummyClassifier, DummyRegressor
from benchmarkwrapper import DummyBenchmark
import typer

class InterfaceSkeleton:
    def __init__(self):
        self.settings = {}
        self.preset = {}

    def loadConfig(self):
        dummy = DummyBenchmark(None)
        self.settings["Dummy"] = dummy.getSettings()
        self.preset["Dummy"] = dummy.getPresets()

    def startBenchmark(self):
        dumClf = DummyClassifier(self.settings["Dummy"], self.preset["Dummy"])
        dumReg = DummyRegressor()
        result = {"classifier":dumClf.dummyClf(),
                  "regressor":dumReg.dummyReg()}
        return result

class displayGUI:
    def __init__(self):
        pass


class displayCLI:
    def __init__(self):
        pass


if __name__ == "__main__":
    ins = InterfaceSkeleton()
    ins.loadConfig()
    ins.startBenchmark()