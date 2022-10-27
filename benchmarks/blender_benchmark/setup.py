#!/usr/bin/env python

import os
import platform
import urllib.request as urllib
import tarfile
import progressbar
from typing import TYPE_CHECKING
import zipfile

if TYPE_CHECKING:
    from typing import Any


class MyProgressBar:
    def __init__(self) -> None:
        self.pbar: "Any" = None

    def __call__(self, block_num: int, block_size: int, total_size: int) -> None:
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
    baseBlenderURL = (
        "https://download.blender.org/release/BlenderBenchmark2.0/launcher/"
    )
    currPath = os.path.dirname(__file__)
    if not os.path.exists(os.path.join(currPath, "bin")):
        os.mkdir(os.path.join(currPath, "bin"))
    filePath = os.path.join(os.path.dirname(__file__), "bin")

    system = platform.system().lower()
    version = "3.0.0"
    extension = "tar.gz"

    if system == "darwin":
        system = "macos"
        extension = "zip"

    url = f"{baseBlenderURL}benchmark-launcher-cli-{version}-{system}.{extension}"
    print(url)

    if not os.path.isfile(os.path.join(filePath, "benchmark-launcher-cli")):
        print("Downloading blender executables:")
        filehandle, _ = urllib.urlretrieve(url, reporthook=MyProgressBar())
        if system == "linux":
            with tarfile.open(filehandle) as tar:
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tar, filePath)
        else:
            with zipfile.ZipFile(filehandle, "r") as zip:
                zip.extractall(filePath)
