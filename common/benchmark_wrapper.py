from abc import ABC, abstractmethod


class BenchmarkWrapper(ABC):
    def __init__(self, benchmarkName):
        self.benchmarkName = benchmarkName

    @abstractmethod
    def startBenchmark(self):
        """Starts the benchmark"""
        pass

    @abstractmethod
    def benchmarkStatus(self):
        """Fetches the status of the current benchmark"""
        pass

    @abstractmethod
    def stopBenchmark(self):
        """Stops the benchmark"""
        pass

    @abstractmethod
    def getSettings(self):
        """Gets the benchmark settings parsing the available ones"""
        pass

    @abstractmethod
    def setSettings(self, settings_file):
        """Sets the benchmark settings according to the users choice"""
        pass
