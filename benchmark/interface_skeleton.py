from typing import Optional
from benchmark_suite import startBenchmark,getBenchmarkConfig 
import typer

class InterfaceSkeleton:
    def __init__(self):
        pass

    def loadConfig(self):
        pass

    def startBenchmark(self):
        pass

    def stopBenchmark(self):
        pass

class displayGUI(InterfaceSkeleton):
    def __init__(self):
        pass


class displayCLI(InterfaceSkeleton):
    def __init__(self):
        pass

class daemon(InterfaceSkeleton):
    def __init__(self):
        pass