import unittest
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from common.benchmark_suite import BenchmarkSuite # noqa: E402
from common.benchmark_wrapper import BenchmarkWrapper # noqa: E402


class TestInheritance(unittest.TestCase):
    def test_class(self):
        self.assertEqual(issubclass(BenchmarkSuite, BenchmarkWrapper), True)


class TestCtor(unittest.TestCase):
    def test_ctor(self):
        with self.assertRaises(FileNotFoundError):
            BenchmarkSuite("./wrongPath")


if __name__ == "__main__":
    unittest.main()
