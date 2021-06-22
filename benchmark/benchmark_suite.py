from benchmark_wrapper import BenchmarkWrapper
import json

class BenchmarkSuite:
    benchmarkArray:BenchmarkWrapper

    def __init__(self):
        self.settings = {}
        self.preset = {}
        self.benchmarkArray = []

    def startBenchmark(self):
        pass

    def benchmarkStatus():
        pass
    
    def stopBenchmark():
        pass

    def getBenchmarkConfig(self):
        with open('../config/benchmarkconfig.json') as f:
            bench_config = json.load(f)
        self.benchmarkArray.gpuUsage = bench_config['gpuUsage']
        #TODO: Proper assignment of which benchmark to run


