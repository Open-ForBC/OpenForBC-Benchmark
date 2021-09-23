from common.benchmark_wrapper import BenchmarkWrapper
import json
import os

class Alessio1Benchmark(benchmarkWrapper): """it's the same class inside benchmark_info.json"""

    def __init__(self):
        self.filePath = os.path.dirname(__file__) """os.path.dirname(__file__) returns the path of this file"""
        pass
    

    def setSettings(self, settings_file):
        settings = os.path.join(self.filePath, "settings", setting_file)

    
    def startBenchmark(self, verbosity=None):


        return {"output": """something to put out"""}

    
    def benchmarkStatus():

        pass


    def getSetting(self):

        pass

    def stopBenchmark():

        pass
