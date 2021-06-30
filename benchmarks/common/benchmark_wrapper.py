from abc import ABC, abstractmethod
from celery.utils.log import get_task_logger
import pathlib


class BenchmarkWrapper(ABC):
    def __init__(self, benchmarkName):
        self.celery_log = get_task_logger(__name__)
        self.benchmarkName = benchmarkName
        self.home_dir = pathlib.Path.cwd()
        self.settings: dict = {}
        self.presets: dict = {}

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
    def setSettings():
        """Gets the benchmark settings according to the users choice"""
        pass

    @abstractmethod
    def getPresets():
        """Accepts presets if any, otherwise sends a null object."""
        pass
