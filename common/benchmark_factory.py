from genericpath import isdir
import importlib
import os
import json
from importlib.machinery import SourceFileLoader


def BenchmarkFactory(benchmark_name, benchmark_settings_file=None):
    base_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "benchmarks"
    )  # Gives path to
    if not os.path.isdir(base_path):
        raise Exception(
            f"The path {base_path} doesn't have directory called benchmarks."
        )
    benchmark_info_path = os.path.join(base_path, benchmark_name, "benchmark_info.json")
    if not os.path.isfile(benchmark_info_path):
        raise Exception("The file path given doesn't exist.")
    try:
        benchmark_info_json = json.load(open(benchmark_info_path, "r"))
    except:
        raise Exception("Can't load the given JSON file")
    try:
        implementation_file = benchmark_info_json["implementation_file"]
        class_name = benchmark_info_json["class_name"]
    except KeyError:
        raise Exception("Key(s) you requested for don't exist.")
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

