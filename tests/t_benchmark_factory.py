import pytest
from common.benchmark_factory import BenchmarkFactory
from common.benchmark_wrapper import BenchmarkWrapper


def test_not_benchmark():
    with pytest.raises(Exception):
        BenchmarkFactory(benchmark_name = 'NotABenchmark',benchmark_settings_file='ficticious_name')

def test_not_settings():
    with pytest.raises(FileNotFoundError):
        BenchmarkFactory(benchmark_name = 'dummy_benchmark',benchmark_settings_file='ficticious_name')

def test_proper_benchmark():
    assert isinstance(BenchmarkFactory(benchmark_name = 'dummy_benchmark',benchmark_settings_file='settings1.json'),BenchmarkWrapper)

def test_empty_benchmark():
    with pytest.raises(TypeError):
        BenchmarkFactory()

def test_missing_argument():
    with pytest.raises(TypeError):
        BenchmarkFactory(benchmark_settings_file='fic_name')
    with pytest.raises(Exception):
        BenchmarkFactory(benchmark_name='No_bench')