# from benchmarks.benchmark_suite.implementation import BenchmarkSuite

# BenchmarkSuite().startBenchmark()
from benchmarks.suites.dummy_benchmark_suite.dummy_suite import DummyBenchmarkSuite

# from user_interfaces.cli import UserMenu
# from benchmarks.dummy_regressor.implementation import DummyRegressor

if __name__ == "__main__":
    DummyBenchmarkSuite().startBenchmark()
    # DummyRegressor().startBenchmark()
    # BenchmarkSuite().startBenchmark()
