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
    This is a dummy benchmark class to demonstrate how to construct code for benchmark implementation.
    """

    def __init__(self):
        self._settings = {}
        self._conversions = {
            'windows':'zip','linux':'tar.gz','macos':'zip'
        }
        self.baseCommand = './benchmark-launcher-cli'
        self.system = platform.system().lower()
        self.url = f'https://download.blender.org/release/BlenderBenchmark2.0/launcher/benchmark-launcher-cli-2.0.4-{self.system}.{self._conversions[self.system]}'
        if not os.path.isfile('benchmark-launcher-cli'):
            filehandle, _ = urllib.urlretrieve(self.url)
            if self.system == 'linux':
                with tarfile.open(filehandle) as h:
                    h.extractall(os.path.dirname(__file__))
            else:
                with zipfile.ZipFile(filehandle, "r") as h:
                    h.extractall(os.path.dirname(__file__))

    def setSettings(self, settings_file):
        self._settings = json.load(open(settings_file, 'r'))

    def startBenchmark(self):
        # result = subprocess.run(self.runable_array)
        return

    def benchmarkStatus():
        pass

    def getSettings(self,command = '',*args):
        self.setSettings('benchmarks/blender_benchmark/settings/settings1.json')
        runCommand = [self.baseCommand,command,*args]
        if not runCommand.__contains__('-b'):
            runCommand += ['-b', str(self._settings["blender_version"])]
        process = subprocess.run(runCommand, check=True, universal_newlines=True)
        if process.returncode == 0:
            return process.stdout
        else:
            return process.stderr
    def stopBenchmark():
        pass

def appendToRunnable(settings:str,runable):
    if not isinstance(settings,type(None)) and settings != '':
        runable.append(settings)
    else:
        pass


'''
##TODO:
[ ] Install the blender version given in settings
[ ] Intuitive way of installing blender scene while showing progress to user


sample running commands:
./benchmark-launcher-cli benchmark bmw27 --blender-version 2.92 --device-type GPU --json 
'''