from common.benchmark_wrapper import BenchmarkWrapper
import json
import os
import torch
import time
import sys


class MatmulBenchmark(BenchmarkWrapper): #it's the same class inside benchmark_info.json

    def __init__(self):
        self.filePath = os.path.dirname(__file__) #os.path.dirname(__file__) returns the path of this file

    def setSettings(self, settings_file):

        settings = os.path.join(self.filePath, "settings", settings_file)
        self.dimension1 = json.load(open(settings, "r"))["dimension1"]
        self.dimension2 = json.load(open(settings, "r"))["dimension2"]
        self.dev = json.load(open(settings, "r"))["device"]

    def startBenchmark(self, verbosity=None):
        returnLog = []

        # check if GPU is available before to try to use it
        if self.dev == "cuda":
            if torch.cuda.is_available():
                print("GPU is available!")
            else:
                print("GPU is not available :(")
                sys.exit(1)

        matrix_1 = torch.randn(self.dimension1, self.dimension2, device=self.dev)
        matrix_2 = torch.randn(self.dimension2, self.dimension1, device=self.dev)

        start_time = time.time()

        torch.matmul(matrix_1, matrix_2)

        multiplication_time = time.time() - start_time

        returnLog.append({self.dev + "multiplication time": multiplication_time})
        print("Product computation time with " + self.dev + " is: %s s" % multiplication_time)

        return {"output": returnLog}

    def benchmarkStatus():
        pass

    def getSettings(self):
        pass

    def stopBenchmark():
        pass
