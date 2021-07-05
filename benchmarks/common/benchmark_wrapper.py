from abc import ABC, abstractmethod
from celery.utils.log import get_task_logger
import pathlib
import time


class BenchmarkWrapper(ABC):
    def __init__(self, benchmarkName):
        self.benchmarkName = benchmarkName
        self.home_dir = pathlib.Path.cwd()
        self._settings = {}

    @abstractmethod
    def startBenchmark():
        """Starts the benchmark"""
        pass

    @abstractmethod
    def benchmarkStatus():
        """Fetches the status of the current benchmark"""
        pass

    @abstractmethod
    def stopBenchmark():
        """Stops the benchmark"""
        pass

    @abstractmethod
    def getSettings():
        """Gets the benchmark settings according to the users choice"""
        pass

    @abstractmethod
    def setSettings():
        """Sets the benchmark settings according to the users choice"""
        pass

    class Timer:
        def __init__(self):
            self.elapsed = float("nan")

        def __enter__(self):
            self._start = time.perf_counter()
            return self

        def __exit__(self, type, value, traceback):
            if value is None:
                self.elapsed = time.perf_counter() - self._start
