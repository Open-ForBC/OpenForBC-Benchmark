from common.benchmark_wrapper import BenchmarkWrapper
import json
import subprocess
import os
import json


class BlenderBenchmark(BenchmarkWrapper):

    """
    This is a Blender benchmark implementation.
    """

    def __init__(self):
        self._settings = {}
        self.filePath = os.path.dirname(__file__)
        self.baseCommand = "bin/benchmark-launcher-cli"

    def setSettings(self, settings_file):
        self._settings = json.load(open(settings_file, "r"))

    def startBenchmark(self, verbosity=None):
        self.getSettings(("blender", "download"))
        self.getSettings(("scenes", "download"))
        self.verbosity = verbosity
        if self.verbosity == None:
            self.verbosity = self._settings["verbosity"]
        try:
            for scene in self._settings["scenes"]:
                startBench = subprocess.run(
                    [
                        os.path.join(self.filePath, self.baseCommand),
                        "benchmark",
                        str(scene),
                        "-b",
                        str(self._settings["blender_version"]),
                        "--device-type",
                        str(self._settings["device_type"]),
                        "--json",
                        "-v",
                        str(self.verbosity),
                    ],stdout=subprocess.PIPE
                )
        except subprocess.CalledProcessError as e:
            print(e.output)
            exit
        if startBench.returncode != 0:
            return startBench.stderr
        else:
            s = startBench.stdout.decode("utf-8")
            s = s[4:-2].replace('false','False')
            s = eval(s)
            returnDict = {}
            specs = ["timestamp","stats","blender_version","benchmark_launcher","benchmark_script","scene"]
            for spec in specs:
                returnDict[spec] = s.get(spec,None)
            return returnDict

    def benchmarkStatus():
        pass

    def getSettings(self, args):
        

    def stopBenchmark():
        pass

