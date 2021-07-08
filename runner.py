# from benchmarks.benchmark_suite.implementation import BenchmarkSuite

# BenchmarkSuite().startBenchmark()
# from benchmarks.benchmark_suite.benchmark_suite import BenchmarkSuite
# import typer
# from user_interfaces import cli

# from user_interfaces import cli
# from benchmarks.dummy_regressor.implementation import DummyRegressor

from common.benchmark_suite import BenchmarkSuite
from common.benchmark_factory import BenchmarkFactory

if __name__ == "__main__":
    BenchmarkSuite(suite_info_path="./suites/example_suite.json").startBenchmark()
    BenchmarkSuite(suite_info_path="./suites/example_suite_2.json").startBenchmark()
    BenchmarkFactory(benchmark_name="dummy_benchmark", benchmark_settings_file="settings1.json").startBenchmark()
    BenchmarkFactory(benchmark_name="dummy_benchmark", benchmark_settings_file="settings2.json").startBenchmark()
    BenchmarkFactory(benchmark_name="dummy_benchmark", benchmark_settings_file="settings2.json").startBenchmark()
    # BenchmarkSuite().startBenchmark()
    # cli.main()
    # InterfaceSkeleton().startBenchmark()
    # DummyRegressor().startBenchmark()
    # BenchmarkSuite().startBenchmark()
