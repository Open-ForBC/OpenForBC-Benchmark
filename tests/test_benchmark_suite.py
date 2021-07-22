import unittest
import os   
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from common.benchmark_wrapper import BenchmarkWrapper
from common.benchmark_suite import BenchmarkSuite


class TestArguments(unittest.TestCase):
    def test_class(self):    
        self.assertEqual(issubclass(BenchmarkSuite,BenchmarkWrapper),True)

    def test_ctor(self):
        with self.assertRaises(FileNotFoundError) or self.assertRaises(Exception):
            BenchmarkSuite('./wrongPath')

    def test_startBenchmark(self):
        with self.assertRaises(AttributeError):
            BenchmarkSuite.startBenchmark("Random_Undefined_Argument")

if __name__ == '__main__':
    unittest.main()