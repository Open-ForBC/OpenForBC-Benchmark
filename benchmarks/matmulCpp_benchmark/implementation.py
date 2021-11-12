from common.benchmark_wrapper import BenchmarkWrapper
import json
import subprocess
import os


class MatmulBenchmarkCpp(BenchmarkWrapper):

    def __init__(self):
        self._settings = {}
        self.filePath = os.path.dirname(__file__)
        self.baseCommand = "bin/matmulCppExe"

    def setSettings(self, settings_file=None):
        if settings_file is None:
            _fileName = json.load(
                open(os.path.join(self.filePath, "benchmark_info.json"), "r")
            )["default_settings"]
            settings_file = os.path.join(self.filePath, "settings", _fileName)
        self._settings = json.load(
            open(os.path.join(self.filePath, "settings", settings_file), "r")
        )

    def startBenchmark(self, verbosity=None):

        #Benchmark execution
        result = subprocess.run(
            [
                os.path.join(self.filePath, self.baseCommand),
                str(self._settings["dimension1"]),
                str(self._settings["dimension2"])
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8"
        )

        print(result.stdout)
        print(result.stderr)

        return {"output": result.stdout}

    def benchmarkStatus():
        pass

    def getSettings(self):
        pass

    def stopBenchmark():
        pass
