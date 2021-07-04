import json
# from ..common.benchmark_factory import BenchmarkFactory
import pathlib
from ..dummy_benchmark_suite.dummy_suite import DummyBenchmarkSuite

class BenchmarkSuite:
    def __init__(self):
        self.settings = {}
        self.preset = {}
        self.benchmarkArray = []
        self.bench_config = {}
        self.home_dir = pathlib.Path.cwd()

    def startBenchmark(self):
        self.getBenchmarkConfig()
        print(self.bench_config)
        # IF STAND-ALONE BENCHMARK =====>

        # for key in self.bench_config.keys():
        #     self.benchmarkArray.append(
        #         BenchmarkFactory().getBenchmarkModule(
        #             file_path=os.path.join("benchmarks", key)
        #         )
        #     )
        # for benchmark in self.benchmarkArray:
        #     run = benchmark.getCallable()
        #     run()

        # ELSE IF BENCHMARK UNDER A SUB-BENCHMARKSUITE ====>

        _runSettings = DummyBenchmarkSuite().prepBenchmark()
        for (run, rep, burnin) in _runSettings:
            for i in range(rep + burnin):
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
            self.bench_config = json.load(config)["benchmarks"]   #ideally if the process is using GPU, you'd be sending in GPU-usage percentage
