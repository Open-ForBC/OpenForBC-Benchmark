from genericpath import isdir
import importlib
import os
import json
from pathlib import Path

def BenchmarkFactory(benchmark_name, benchmark_settings_file=None):
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "benchmarks")       #Gives path to
    if not Path.is_dir(base_path):
        raise Exception("The path given doesn't exist.")
    benchmark_info_path = os.path.join(base_path, benchmark_name, "benchmark_info.json")
    if not Path.is_file(benchmark_info_path):
        raise Exception("The file path given doesn't exist.")
    benchmark_info_json = json.load(open(benchmark_info_path, "r"))
    from importlib.machinery import SourceFileLoader
    implementation_file = benchmark_info_json["implementation_file"]
    class_name = benchmark_info_json["class_name"]
    module = SourceFileLoader(  
        "{}.{}".format(implementation_file, class_name),
        os.path.join(os.path.dirname(benchmark_info_path), implementation_file),
    ).load_module()
    benchmark = eval("module.{}()".format(class_name))
    if benchmark_settings_file is not None:
        benchmark.setSettings(
            os.path.join(
                os.path.dirname(benchmark_info_path),
                "settings",
                benchmark_settings_file,
            )
        )
        return benchmark
    else:
        raise Exception(
            "Cannot find {} benchmark or benchmark_info.json. ".format(benchmark_name)
        )
