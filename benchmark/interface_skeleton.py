from dummy import DummyClassifier
from benchmarkwrapper import DummyBenchmark
import typer

class InterfaceSkeleton:
    def __init__(self):
        self.settings = {}
        self.preset = {}

    def loadConfig(self):
        dummy = DummyBenchmark(None)
        self.settings = dummy.getSettings()
        self.preset = dummy.getPresets()

    def startBenchmark(self):
        dumClf = DummyClassifier(self.settings, self.preset)
        print(dumClf.dummyClf())


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
