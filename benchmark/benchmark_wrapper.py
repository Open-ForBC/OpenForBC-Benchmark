from abc import ABC, abstractmethod
from sys import path
from typing import Any
import json
import os


class BenchmarkWrapper(ABC):
    def __init__(self, gpuUsage: Any):
        self.gpuUsage = gpuUsage
        self.settings: dict = {}
        self.presets: dict = {}

    @abstractmethod
    def startBenchmark():
        """ Starts the benchmark """
        pass

    @abstractmethod
    def benchmarkStatus():
        """ Fetches the status of the current benchmark """
        pass

    @abstractmethod
    def stopBenchmark():
        """ Stops the benchmark """
        pass

    @abstractmethod
    def getSettings():
        """Gets the benchmark settings according to the users choice"""
        pass

    @abstractmethod
    def getPresets():
        """ Accepts presets if any, otherwise sends a null object."""
        pass

