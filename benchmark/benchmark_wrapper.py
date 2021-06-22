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


class DummyBenchmark(BenchmarkWrapper):
    def __init__(self, gpuUsage: Any):
        super().__init__(gpuUsage)
        self.dir = os.path.dirname(__file__)

    def getSettings(self):
        with open(os.path.join(self.dir,"../config/dummy_config.json"))as f:
            settings = json.load(f)
        return settings

    def getPresets(self):
        with open(os.path.join(self.dir,"../config/dummy_preset.json")) as f:
            presets = json.load(f)
        return presets

    def startBenchmark():
        pass

    def benchmarkStatus():
        pass

    def stopBenchmark():
        pass