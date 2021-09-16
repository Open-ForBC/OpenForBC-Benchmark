from common.benchmark_wrapper import BenchmarkWrapper
import json
import subprocess
import os


class BlenderBenchmark(BenchmarkWrapper):

    """
    This is a Blender benchmark implementation.
    """

    def __init__(self):
        self._settings = {}
        self.filePath = os.path.dirname(__file__)
        self.baseCommand = "bin/benchmark-launcher-cli"

    def setSettings(self, settings_file=None):
        if settings_file is None:
            _fileName = json.load(
                open(os.path.join(self.filePath, "benchmark_info.json"), "r")
            )["default_settings"]
            settings_file = os.path.join(self.filePath, "settings", _fileName)
        self._settings = json.load(
            open(os.path.join(self.filePath, "settings", settings_file), "r")
        )
        try:
            subprocess.run(  # Downloads blender version listed in benchmark_info.json
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
            subprocess.run(  # Downloads scenes listed in benchmark_info.json
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
        returnLog = []  # List for returning to logging func
        self.verbosity = verbosity

        if self.verbosity is None:
            self.verbosity = self._settings["verbosity"]
        print("Running Benchmark......")

        for scene in self._settings["scenes"]:
            print(f"Benchmarking Scene: {scene}")
            res = subprocess.run(
                [  # Subprocess to run the benchmark
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

            if res.stderr or res.returncode != 0:  # Error catching
                print(f"Blender-benchmark scene: {scene} exited with non zero error")
                returnLog.append({"scene": scene, "run": "Unsuccessful"})
                continue

            s = res.stdout.decode("utf-8")  # get output in proper formatting
            s = s[4:-2].replace("false", "False")  # Replace to use with eval
            s = eval(s)  # Converting to a dictionary
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
                returndict[spec] = s.get(spec, None)
            returnLog.append(returndict)
        return {"output": returnLog}

    def benchmarkStatus():
        pass

    def getSettings(self):
        """
        Gets the settings for the benchmark
        """
        pass

    def stopBenchmark():
        pass
