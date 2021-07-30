import os
import platform
import urllib.request as urllib
import tarfile
import zipfile


if __name__ == "__main__":
    currPath = os.path.dirname(__file__)
    if not os.path.exists(os.path.join(currPath, "bin")):
        os.mkdir(os.path.join(currPath, "bin"))
    filePath = os.path.join(os.path.dirname(__file__), "bin")
    system = platform.system().lower()
    if system == "linux":
        url = "https://download.blender.org/release/BlenderBenchmark2.0/launcher/benchmark-launcher-cli-2.0.5-linux.tar.gz"
    else:
        url = f"https://download.blender.org/release/BlenderBenchmark2.0/launcher/benchmark-launcher-cli-2.0.4-{system}.zip"
    if not os.path.isfile(os.path.join(filePath, "benchmark-launcher-cli")):
        filehandle, _ = urllib.urlretrieve(url)
        if system == "linux":
            with tarfile.open(filehandle) as h:
                h.extractall(filePath)
        else:
            with zipfile.ZipFile(filehandle, "r") as h:
                h.extractall(filePath)
