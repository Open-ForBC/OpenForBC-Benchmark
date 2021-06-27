import benchmark
from typing import Optional
from benchmark_suite import BenchmarkSuite
import typer


class InterfaceSkeleton:
    def __init__(self):
        self.BenchSuite = BenchmarkSuite()

    def loadConfig(self):
        return self.BenchSuite.getBenchmarkConfig()

    def startBenchmark(self):
        return self.BenchSuite.startBenchmark()

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


##############################################
