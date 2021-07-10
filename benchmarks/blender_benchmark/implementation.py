from common.benchmark_wrapper import BenchmarkWrapper
import json
import urllib.request as urllib
import subprocess
import tarfile
import platform
import os
import zipfile


class BlenderBenchmark(BenchmarkWrapper):

    """
    This is a Blender benchmark implementation.
    """

    def __init__(self):
        self._settings = {}
        self.filePath = os.path.dirname(__file__)
        self.baseCommand = "benchmark-launcher-cli"
        self.system = platform.system().lower()
        if self.system == "linux":
            self.url = "https://download.blender.org/release/BlenderBenchmark2.0/launcher/benchmark-launcher-cli-2.0.5-linux.tar.gz"
        else:
            self.url = f"https://download.blender.org/release/BlenderBenchmark2.0/launcher/benchmark-launcher-cli-2.0.4-{self.system}.zip"
        if not os.path.isfile(os.path.join(self.filePath, "benchmark-launcher-cli")):
            filehandle, _ = urllib.urlretrieve(self.url)
            if self.system == "linux":
                with tarfile.open(filehandle) as h:
                    h.extractall(self.filePath)
            else:
                with zipfile.ZipFile(filehandle, "r") as h:
                    h.extractall(self.filePath)

    def setSettings(self, settings_file):
        self._settings = json.load(open(settings_file, "r"))
        self.getSettings("blender_download")
        self.getSettings("scenes_download")

    def startBenchmark(self):
        try:
            startBench = subprocess.run(
                [
                    os.path.join(self.filePath, self.baseCommand),
                    "benchmark",
                    str(self.scenes),
                    "-b",
                    str(self._settings["blender_version"]),
                    "--device-type",
                    str(self._settings["device_type"]),
                    "--json",
                ]
            )
        except subprocess.CalledProcessError as e:
            print(e.output)
            exit

        if startBench.returncode == 0:
            print(startBench.stdout)
        else:
            print(startBench.stderr)

    def benchmarkStatus():
        pass

    def getSettings(self, args):
        print(args)
        commands = {
            "blender_download": [
                os.path.join(self.filePath, self.baseCommand),
                "blender",
                "download",
                str(self._settings["blender_version"]),
            ],
            "blender_list": [
                os.path.join(self.filePath, self.baseCommand),
                "blender",
                "list",
            ],
            "compatible_devices": [
                os.path.join(self.filePath, self.baseCommand),
                "devices",
                "-b",
                str(self._settings["blender_version"]),
            ],
            "help": [os.path.join(self.filePath, self.baseCommand), "--help"],
            "scenes_download": [
                os.path.join(self.filePath, self.baseCommand),
                "scenes",
                "download",
                "-b",
                str(self._settings["blender_version"]),
            ]
            + (self._settings["scenes"]),
            "scene_list": [
                os.path.join(self.filePath, self.baseCommand),
                "scenes",
                "list",
                "-b",
                str(self._settings["blender_version"]),
            ],
            "clear_cache": [
                os.path.join(self.filePath, self.baseCommand),
                "clear_cache",
            ],
        }
        try:
            process = subprocess.run(
                commands.get(args, "nothing"), check=True, universal_newlines=True
            )
        except subprocess.CalledProcessError as e:
            print(e.output)
        if process.returncode != 0:
            raise process.stderr

    def stopBenchmark():
        pass
