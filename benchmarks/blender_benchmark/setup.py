import os
import platform
import urllib.request as urllib
import tarfile
import progressbar
import zipfile


class MyProgressBar():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar = progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()


if __name__ == "__main__":
    print("Initialising setup......")
    baseBlenderURL = "https://download.blender.org/release/BlenderBenchmark2.0/launcher/"
    currPath = os.path.dirname(__file__)
    if not os.path.exists(os.path.join(currPath, "bin")):
        os.mkdir(os.path.join(currPath, "bin"))
    filePath = os.path.join(os.path.dirname(__file__), "bin")
    system = platform.system().lower()
    if system == "linux":
        url = baseBlenderURL + "benchmark-launcher-cli-2.0.5-linux.tar.gz"
    else:
        url = baseBlenderURL + f"benchmark-launcher-cli-2.0.4-{system}.zip"
    if not os.path.isfile(os.path.join(filePath, "benchmark-launcher-cli")):
        print("Downloading blender executables:")
        filehandle, _ = urllib.urlretrieve(url, reporthook=MyProgressBar())
        if system == "linux":
            with tarfile.open(filehandle) as h:
                h.extractall(filePath)
        else:
            with zipfile.ZipFile(filehandle, "r") as h:
                h.extractall(filePath)
