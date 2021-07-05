from ..dummy_classifier.implementation import DummyClassifier
from ..dummy_regressor.implementation import DummyRegressor
from ..common.benchmark_factory import BenchmarkFactory
import os
import sys
from pathlib import Path
import functools
import logging

logging.basicConfig(
    level=logging.INFO,
    filename="logs/bench.log",
    filemode="w",
    format="%(asctime)s-%(process)d-%(levelname)s-%(message)s",
)


class DummyBenchmarkSuite:
    def __init__(self) -> None:
        self._runSettings = []
        self.benchs = [DummyClassifier(), DummyRegressor()]

    def getModule(self, key):
        return BenchmarkFactory().getBenchmarkModule(file_path=key)

    def prepBenchmark(self):
        for benchs in self.benchs:
            burnin, repetitions = benchs.getSettings()
            run = functools.partial(benchs.startBenchmark)
            if repetitions is None:
                fileName = str(
                    Path(sys.modules[benchs.__module__].__file__).parent
                ).split("/")[-1]
                newFile = os.path.join("benchmarks/", fileName)
                try:
                    _callable = self.getModule(newFile)
                except ImportError:
                    print("can't get callable function")
                run, repetitions = _callable.getCallable()
            self._runSettings.append((run, repetitions, burnin))
        return self._runSettings
