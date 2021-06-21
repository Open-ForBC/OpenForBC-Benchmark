from abc import ABC, abstractmethod
from typing import Any
import json


class BenchmarkWrapper(ABC):
    def __init__(self, gpuUsage: Any):
        self.gpuUsage = gpuUsage
        self.settings: dict = {}
        self.presets: dict = {}

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

    def getSettings(self):
        with open("config/dummy_config.json") as f:
            settings = json.load(f)
        return settings

    def getPresets(self):
        with open("config/dummy_preset.json") as f:
            presets = json.load(f)
        return presets
