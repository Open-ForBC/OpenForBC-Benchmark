import importlib
import os
import math
from benchmark_wrapper import BenchmarkWrapper
import json

def BenchmarkFactory(benchmark_name, benchmark_settings_file):
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "benchmarks")
    benchmark_info_path = os.path.join(base_path, benchmark_name, "benchmark_info.json")
    if os.path.isfile(benchmark_info_path):
        benchmark_info_json = json.load(open(benchmark_info_path, 'r'))
        from importlib.machinery import SourceFileLoader
        implementation_file = benchmark_info_json["implementation_file"]
        class_name = benchmark_info_json["class_name"]
        module = SourceFileLoader('{}.{}'.format(implementation_file, class_name),
                               os.path.join(os.path.dirname(benchmark_info_path), implementation_file)).load_module()
        benchmark = eval("module.{}()".format(class_name))
        benchmark.setSettings(os.path.join(os.path.dirname(benchmark_info_path), 'settings', benchmark_settings_file))
        return benchmark
    else:
        raise Exception("Cannot find {} benchmark or benchmark_info.json. ".format(benchmark_name))

if __name__=="__main__":
    bench = BenchmarkFactory('dummy_benchmark')
    bench.startBenchmark()