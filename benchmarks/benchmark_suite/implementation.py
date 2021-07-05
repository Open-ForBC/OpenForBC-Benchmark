# from benchmarks.dummy_classifier import getCallable
import json
import os
from ..common.benchmark_factory import BenchmarkFactory
import pathlib

# from ..dummy_benchmark_suite.dummy_suite import DummyBenchmarkSuite
import logging

logger = logging.getLogger(__name__)

logger.setLevel(logging.WARNING)


class BenchmarkSuite:
    def __init__(self):
        # self.file_handler = logging.FileHandler('logfile.log')
        # self.formatter = logging.Formatter(format='%(asctime)s-%(process)d-%(levelname)s-%(message)s')
        # self.file_handler.setFormatter(self.formatter)
        self.settings = {}
        self.preset = {}
        self.benchmarkArray = []
        self.bench_config = {}
        self.home_dir = pathlib.Path.cwd()

    def startBenchmark(self):
        self.getBenchmarkConfig()
        for key in self.bench_config:
            _bmarkObj = BenchmarkFactory().getBenchmarkModule(
                file_path=os.path.join("benchmarks", key)
            )
            _ans, _parent = _bmarkObj.isStandAlone()
            # IF STAND-ALONE BENCHMARK =====>
            if _ans == "True":
                run, rep = _bmarkObj.getCallable()
                burnin = _bmarkObj.hasBurnin()
                _arrObj = run, rep, burnin
            # ELSE GROUPED BENCHMARK ======>
            else:
                _bmObj = BenchmarkFactory().getBenchmarkModule(
                    file_path=os.path.join("benchmarks", _parent)
                )
                _obj = _bmObj.getCallable()
                _arrObj = _obj.prepBenchmark()
        self.benchmarkArray.append(_arrObj)
        for elements in self.benchmarkArray:
            for run, rep, burnin in elements:
                for _ in range(rep + burnin):
                    results, timeElapsed = run()
                    print(f"Results:{results} \nTime Elapsed:{timeElapsed}")

    def benchmarkStatus():
        pass

    def stopBenchmark():
        pass

    def getBenchmarkConfig(self):
        with open(
            pathlib.Path.cwd().joinpath(
                "benchmarks", "benchmark_suite", "suite_info.json"
            )
        ) as config:
            self.bench_config = json.load(config)[
                "benchmarks"
            ]  # ideally if the process is using GPU, you'd be sending in GPU-usage percentage
