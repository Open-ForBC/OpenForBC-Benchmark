from common.benchmark_wrapper import BenchmarkWrapper
import json
import os
import torch
import time


class MatmulBenchmark(BenchmarkWrapper): #it's the same class inside benchmark_info.json

    def __init__(self):
        self.filePath = os.path.dirname(__file__) #os.path.dirname(__file__) returns the path of this file

    def setSettings(self, settings_file):
        """
        Open and read the settings file
        """
        settings = os.path.join(self.filePath, "settings", settings_file)
        self.dimension1 = json.load(open(settings, "r"))["dimension1"]
        self.dimension2 = json.load(open(settings, "r"))["dimension2"]

    def startBenchmark(self, verbosity=None):

        start_time = time.time()

        print("The first matrix has dimensions", self.dimension1, "x", self.dimension2)
        print("The second matrix has dimensions", self.dimension2, "x", self.dimension1)

        matrix_1 = torch.randn(self.dimension1, self.dimension2, device="cpu")
        matrix_2 = torch.randn(self.dimension2, self.dimension1, device="cpu")

        product = torch.matmul(matrix_1, matrix_2)

        print("The product of the two matrices has dimensions ", product.shape[0], "x", product.shape[1])
        print("The product has been performed in %s using CPU" % (time.time() - start_time))

        matrix_1 = matrix_1.to("cuda:0")
        matrix_2 = matrix_2.to("cuda:0")
        product = torch.matmul(matrix_1, matrix_2)

        print("The product of the two matrices has dimensions ", product.shape[0], "x", product.shape[1])
        print("The product has been performed in %s using GPU" % (time.time() - start_time))

        return {"output": time.time() - start_time} #Where does this output go?

    def benchmarkStatus():
        pass

    def getSettings(self):
        pass

    def stopBenchmark():
        pass
