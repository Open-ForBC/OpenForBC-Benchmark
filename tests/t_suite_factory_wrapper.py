from common.benchmark_factory import BenchmarkFactory
from common.benchmark_wrapper import BenchmarkWrapper
from benchmarks.dummy_benchmark.implementation import DummyBenchmark
import pytest

@pytest.fixture
def diff_benches():
    return [DummyBenchmark(),DummyBenchmark()]

# def test_diff_benches(diff_benches):
#     bmark = 
