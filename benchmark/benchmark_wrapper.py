from abc import ABC, abstractmethod
from sys import path
from typing import Any
import json
import os
from celery.utils.log import get_task_logger


class BenchmarkWrapper(ABC):
    def __init__(self, benchmarkName, gpuUsage: Any):
        self.celery_log = get_task_logger(__name__)
        self.benchmarkName = benchmarkName
        self.gpuUsage = gpuUsage
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
    def getSettings():
        """Gets the benchmark settings according to the users choice"""
        pass

    @abstractmethod
    def getPresets():
        """Accepts presets if any, otherwise sends a null object."""
        pass
