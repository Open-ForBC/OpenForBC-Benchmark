from ..dummy_classifier.implementation import DummyClassifier
from ..dummy_regressor.implementation import DummyRegressor
from ..common.benchmark_factory import estimate_repetitions, BenchmarkFactory
import os
import functools


class DummyBenchmarkSuite:
    def __init__(self) -> None:
        self._runSettings = []
        self.benchs = [DummyClassifier(), DummyRegressor()]

    def getModule(self, key):
        return BenchmarkFactory().getBenchmarkModule(
            file_path=os.path.join("benchmarks", key)
        )

    def prepBenchmark(self):
        print("in prepBench")
        for benchs in self.benchs:
            # bench = self.getModule(benchs)
            burnin, repetitions = benchs.setSettings()
            print(benchs)
            run = functools.partial(benchs.startBenchmark)
            # if repetitions is None:
            #     run = bench.getCallable()
            #     print(bench.getCallable())
            #     repetitions = estimate_repetitions(run)
            self._runSettings.append((run, repetitions, burnin))
        return self._runSettings

        # for key in self.bench_config.keys():
        #     self.benchmarkArray.append(
        #         BenchmarkFactory().getBenchmarkModule(
        #             file_path=os.path.join("benchmarks", key)
        #         )
        #     )
        # for benchmark in self.benchmarkArray:
        #     run = benchmark.getCallable()
        #     run()
