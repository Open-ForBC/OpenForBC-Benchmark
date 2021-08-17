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

    def setSettings(self, settings_file = None):
        if settings_file == None:
            _fileName = json.load(open("benchmarks/blender_benchmark/benchmark_info.json","r"))["default_settings"]
            settings_file = os.path.join(self.filePath,"settings",_fileName)
        self._settings = json.load(open(settings_file, "r"))
        try:
            download_blender = subprocess.run(  #Downloads blender version listed in benchmark_info.json
                [
                    os.path.join(self.filePath, self.baseCommand),
                    "blender",
                    "download",
                    str(self._settings["blender_version"]),
                ],
                stdout=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as e:
            return f"{e}: Can't download blender version listed in benchmark_info.json"
        try:
            download_scenes = subprocess.run(   #Downloads scenes listed in benchmark_info.json
                [
                    os.path.join(self.filePath, self.baseCommand),
                    "scenes",
                    "download",
                    "-b",
                    str(self._settings["blender_version"]),
                ]
                + (self._settings["scenes"]),
                stdout=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as e:
            return f"{e}: Can't download blender scene(s) listed in benchmark_info.json"

    def startBenchmark(self, verbosity=None):
        """
            Method defination for starting the benchmark
        """
        returnLog = []
        self.setSettings()
        self.verbosity = verbosity
        if self.verbosity == None:
            self.verbosity = self._settings["verbosity"]
        for scene in self._settings["scenes"]:
            try:
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
                    ],
                    stdout=subprocess.PIPE,
                )
            except subprocess.CalledProcessError as e:
                return f"{e.output}: Can't run the blender-benchmark."
            s = startBench.stdout.decode("utf-8")
            s = s[4:-2].replace('false','False')
            s = eval(s)
            returndict = {}
            specs = [
              "timestamp",
              "stats",
              "blender_version",
              "benchmark_launcher",
              "benchmark_script",
              "scene",
            ]
            for spec in specs:
                returndict[spec] = s.get(spec,None)
            returnLog.append(returndict)
        return {"output":returnLog}

    def benchmarkStatus():
        pass

    def getSettings(self):
        """
        Gets the settings for the benchmark
        """
        pass

    def stopBenchmark():
        pass
