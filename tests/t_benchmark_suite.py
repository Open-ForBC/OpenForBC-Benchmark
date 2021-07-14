from common.benchmark_wrapper import BenchmarkWrapper
from common.benchmark_suite import BenchmarkSuite
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
def testSuite():    
    assert issubclass(BenchmarkSuite,BenchmarkWrapper) == True
    BenchmarkSuite(suite_info_path="./suites/example_suite.json") == None
    
