from importlib.machinery import SourceFileLoader
import os
import json


def BenchmarkFactory(benchmark_name, benchmark_settings_file=None):
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "benchmarks")
    benchmark_info_path = os.path.join(base_path, benchmark_name, "benchmark_info.json")
    if not os.path.isfile(benchmark_info_path):
        raise Exception("The file path given doesn't exist.")
    with open(benchmark_info_path, "r") as file:
        try:
            benchmark_info_json = json.load(file)
        except IOError:
            raise Exception("Can't load the given JSON file")

    implementation_file = benchmark_info_json["implementation_file"]
    class_name = benchmark_info_json["class_name"]
    module = SourceFileLoader( # noqa: F841
        "{}.{}".format(implementation_file, class_name),
        os.path.join(os.path.dirname(benchmark_info_path), implementation_file),
    ).load_module()
    benchmark = eval("module.{}()".format(class_name))
    if benchmark_settings_file is not None:
        benchmark.setSettings(benchmark_settings_file)
    return benchmark
