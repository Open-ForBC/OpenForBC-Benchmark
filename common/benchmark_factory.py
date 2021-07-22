import os
import json
from importlib.machinery import SourceFileLoader


def BenchmarkFactory(benchmark_name, benchmark_settings_file=None):
    """
    Factory method to provide benchmark object.
    """
    base_path = os.path.join(  # Gets the general path for all benchmarks
        os.path.dirname(os.path.dirname(__file__)), "benchmarks"
    )

    if not os.path.isdir(base_path):  # Check: benchmarks in basePath
        raise Exception(
            f"The path {base_path} doesn't have directory called benchmarks."
        )

    benchmark_info_path = os.path.join(base_path, benchmark_name, "benchmark_info.json")

    if not os.path.isfile(
        benchmark_info_path
    ):  # Check: benchmark_info.json exist in path
        raise Exception("The file path given doesn't exist.")

    with open(benchmark_info_path, "r") as file:
        try:
            benchmark_info_json = json.load(file)
        except:
            raise Exception("Can't load the given JSON file")

    try:
        implementation_file = benchmark_info_json["implementation_file"]
        class_name = benchmark_info_json["class_name"]
    except KeyError as e:
        raise Exception(f"{e}: Key(s) you requested for don't exist.")

    module = SourceFileLoader(  # Imports the module from given file
        "{}.{}".format(implementation_file, class_name),
        os.path.join(os.path.dirname(benchmark_info_path), implementation_file),
    ).load_module()
    benchmark = eval("module.{}()".format(class_name))  # <Parses and runs class_name>

    if (
        benchmark_settings_file is not None
    ):  # Check: settings file given to the function
        try:  # call the setSettings in the corresponding benchmark
            benchmark.setSettings(
                os.path.join(
                    os.path.dirname(benchmark_info_path),
                    "settings",
                    benchmark_settings_file,
                )
            )
        except:
            raise Exception("Settings were unsucessful")

    return benchmark
