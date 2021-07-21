import unittest
from typer.testing import CliRunner
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from user_interfaces import cli

runner = CliRunner()

class TestArguments(unittest.TestCase):
    # def setUp(self):
        
    def invokeFactory(self,arr):                                                                #Function that invokes the method defined in the CLI app
        return runner.invoke(cli.app,arr)   

    def test_helper(self):                                                                      #Tests main help command for CLI
        assert self.invokeFactory(["--help"]).exit_code == 0
  
    def test_listing(self): 
        assert self.invokeFactory(["list-benchmarks"]).exit_code == 0 
        assert self.invokeFactory(["list-suites"]).exit_code == 0 
        assert self.invokeFactory(["list-suites","randomString"]).exit_code != 0 
        assert self.invokeFactory(["list-benchmarks","randomString"]).exit_code != 0 


    def test_run_benchmark(self):
        assert "Error: Missing option" in self.invokeFactory(["run-benchmark"]).stdout  
        assert self.invokeFactory(["run-benchmark","-b","dummy_benchmark","-s","settings1.json"]).exit_code == 0 
        assert "implementation doesn't exist" in self.invokeFactory(["run-benchmark","-b","bad benchmark"]).stdout
        assert self.invokeFactory(["run-benchmark","--help"]).exit_code == 0 
        #TODO:test other features such as verbosity etc.

    def test_run_suite(self):
        # assert "Error: Missing option" in self.invokeFactory(["run-suite"]).stdout     
        assert self.invokeFactory(["run-suite","example_suite.json"]).exit_code == 0 
        assert self.invokeFactory(["run-suite","notAsuite.json"]).exit_code != 0 and "implementation doesn't exist" in self.invokeFactory(["run-suite","notAsuite.json"]).stdout 

    def test_get_settings(self):
        assert self.invokeFactory(["get-settings","blender_benchmark","scenes","list"]).exit_code == 0 
        assert self.invokeFactory(["get-settings","noBenchmark","noSettings"]).exit_code != 0

    
if __name__ == '__main__':
    unittest.main()