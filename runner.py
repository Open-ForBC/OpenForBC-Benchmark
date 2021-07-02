from benchmarks.benchmark_suite.implementation import BenchmarkSuite

# BenchmarkSuite().startBenchmark()

from user_interfaces.cli import UserMenu

# from benchmarks.dummy_regressor.implementation import DummyRegressor

if __name__ == "__main__":
    UserMenu().runner()
    # DummyRegressor().startBenchmark()
    # BenchmarkSuite().startBenchmark()
