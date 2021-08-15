import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from common.benchmark_factory import BenchmarkFactory
from common.benchmark_wrapper import BenchmarkWrapper


class TestArguments(unittest.TestCase):
    def test_not_benchmark(self):
        with self.assertRaises(Exception):
            BenchmarkFactory(
                benchmark_name="NotABenchmark",
                benchmark_settings_file="ficticious_name",
            )

    def test_not_settings(self):
        with self.assertRaises(FileNotFoundError):
            BenchmarkFactory(
                benchmark_name="dummy_benchmark",
                benchmark_settings_file="ficticious_name",
            )

class TestObjectType(unittest.TestCase):
    def test_proper_benchmark(self):
        self.assertTrue(
            isinstance(
                BenchmarkFactory(
                    benchmark_name="dummy_benchmark",
                    benchmark_settings_file="settings1.json",
                ),
                BenchmarkWrapper,
            )
        )

if __name__ == "__main__":
    unittest.main()
