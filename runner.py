# from common.benchmark_wrapper import BenchmarkWrapper
# from common.benchmark_suite import BenchmarkSuite
from common.benchmark_factory import BenchmarkFactory
# from benchmarks.blender_benchmark.implementation import BlenderBenchmark


if __name__ == "__main__":
    # BenchmarkSuite(suite_info_path="./suites/example_suite.json").startBenchmark()
    # BenchmarkSuite(suite_info_path="./suites/example_suite_2.json").startBenchmark()
    # BenchmarkFactory(benchmark_name="dummy_benchmark", benchmark_settings_file="settings1.json").startBenchmark()
    # BenchmarkFactory(benchmark_name="dummy_benchmark", benchmark_settings_file="settings2.json").startBenchmark()
    # BenchmarkFactory(benchmark_name="dummy_benchmark", benchmark_settings_file="settings2.json").startBenchmark()
    BenchmarkFactory(
        benchmark_name="blender_benchmark", benchmark_settings_file="settings1.json"
    ).startBenchmark()
