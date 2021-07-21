from common.benchmark_wrapper import BenchmarkWrapper
from common.benchmark_suite import BenchmarkSuite
import pytest
from pathlib import Path


# @pytest.fixture
# def ctor(path):
#     BenchmarkSuite('./wrongPath').startBenchmark()


def test_Suite():    
    assert issubclass(BenchmarkSuite,BenchmarkWrapper) == True

def test_ctor():
    with pytest.raises(FileNotFoundError):
        BenchmarkSuite('./wrongPath').startBenchmark()


def test_startBenchmark():
    BenchmarkSuite(suite_info_path="./suites/example_suite_2.json").startBenchmark()

# def test_