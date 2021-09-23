from common.benchmark_wrapper import BenchmarkWrapper
import json
import os

class Alessio1Benchmark(benchmarkWrapper): #it's the same class inside benchmark_info.json

    def __init__(self):
        self.filePath = os.path.dirname(__file__) #os.path.dirname(__file__) returns the path of this file
        
    

    def setSettings(self, settings_file):
        """
        Open and read the settings file
        """
        settings = os.path.join(self.filePath, "settings", settings_file)
        self.dimension1 = json.load(open(settings, "r"))[dimension1]
        self.dimension2 = json.load(open(settings, "r"))[dimension2]

    
    def startBenchmark(self, verbosity=None):
        
        print("The first dimension of the matrix is equal to", self.dimension1)

        return {"output": #something to put out} #Where does this output go?

    
    def benchmarkStatus():

        pass


    def getSetting(self):

        pass

    def stopBenchmark():

        pass
