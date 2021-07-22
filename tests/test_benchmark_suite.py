import unittest
from common.benchmark_wrapper import BenchmarkWrapper
from common.benchmark_suite import BenchmarkSuite


class TestArguments(unittest.TestCase):
    def test_class(self):    
        self.assertEqual(issubclass(BenchmarkSuite,BenchmarkWrapper),True)

    def test_ctor(self):
        with self.assertRaises(FileNotFoundError):
            BenchmarkSuite('./wrongPath')