#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, Optional

PACKAGES_JSON_FILENAME = "packages.json"


class ProgressBar:
    def __init__(self, total_size):
        from progressbar import Bar, ETA, FileTransferSpeed, Percentage, UnknownLength

        self.pbar = None
        self.total_size = total_size if total_size > 0 else UnknownLength
        self.widgets = [
            Percentage() if total_size else " ",
            Bar(),
            " ",
            FileTransferSpeed(),
            " ",
            " (",
            ETA(),
            ") ",
        ]

    def call(self, block_num, block_size):
        from progressbar import ProgressBar, UnknownLength

        if not self.pbar:
            self.pbar = ProgressBar(maxval=self.total_size, widgets=self.widgets)
            self.pbar.start()

        downloaded = block_num * block_size

        if self.total_size == UnknownLength:
            self.pbar.update(downloaded)
        else:
            if downloaded < self.total_size:
                self.pbar.update(downloaded)
            else:
                self.pbar.finish()


@dataclass
class PhoronixDownloadDefinition:
    filename: str
    platform: Optional[Literal["darwin", "linux", "windows"]]
    urls: list[str]
    size: Optional[int] = None
    md5: Optional[str] = None
    sha256: Optional[str] = None

    @classmethod
    def from_json(cls, filename: str) -> list[PhoronixDownloadDefinition]:
        from json import load

        with open(filename, "r") as file:
            packages = load(file)
            assert isinstance(packages, list)

            return [cls(**package) for package in packages]

    @staticmethod
    def into_json(packages: list[PhoronixDownloadDefinition], filename: str) -> None:
        from json import dump

        with open(filename, "w") as file:
            dump([package.__dict__ for package in packages], file)

    def __repr__(self) -> str:
        return (
            f"{self.filename} (platform={self.platform}, "
            f"{'md5' if self.md5 else 'sha256' if self.sha256 else 'size' if self.size else 'noverify'}"
            f"={self.md5 or self.sha256 or self.size or '1'})"
        )


def mycopyfileobj(fsrc, fdst, length=0, total_size=0, prog_bar: ProgressBar = None):
    """copy data from file-like object fsrc to file-like object fdst"""
    from shutil import COPY_BUFSIZE

    # Localize variable access to minimize overhead.
    if not prog_bar:
        prog_bar = ProgressBar(total_size)
    if not length:
        length = COPY_BUFSIZE
    fsrc_read = fsrc.read
    fdst_write = fdst.write
    block_num = 0
    while True:
        block_num += 1
        buf = fsrc_read(length)
        if not buf:
            break
        fdst_write(buf)
        prog_bar.call(block_num=block_num, block_size=length)


def download_file(url, target_filename):
    from requests import get

    with get(url, stream=True) as r:
        try:
            total_size = int(r.headers.get("Content-Length"))
        except Exception:
            total_size = 0
        with open(target_filename, "wb") as f:
            mycopyfileobj(r.raw, f, total_size=total_size)


def download_packages():
    """
    A function which downloads the required software as described by get_download_packages().
    It verifies the checksums afterwards.
    """
    from hashlib import md5, sha256
    from os import remove
    from os.path import exists, isfile, getsize
    from sys import platform
    from traceback import print_exc

    if not exists(PACKAGES_JSON_FILENAME):
        return

    packages = PhoronixDownloadDefinition.from_json(PACKAGES_JSON_FILENAME)

    for package in packages:
        hash = package.md5 or package.sha256
        hash_fn = md5 if package.md5 else sha256 if package.sha256 else None

        if package.platform and package.platform != platform:
            print(f"Skipping {package}, not required for platform {platform}.")
            continue

        print(f"Downloading {package}")

        target_file = package.filename

        if isfile(target_file):
            with open(target_file, "rb") as f:
                if (hash and hash_fn(f.read()).hexdigest() == hash) or getsize(
                    target_file
                ) == package.size:
                    print(f"File {target_file} verified, skipping download.")
                    continue

                print(f"Deleting non-verified file: {target_file}")
                remove(target_file)

        downloaded = False
        for url in package.urls:
            print(url)
            try:
                download_file(url=url, target_filename=target_file)
            except Exception:
                print_exc()
                continue

            if hash:
                actual_hash = hash_fn(open(target_file, "rb").read()).hexdigest()
                verified = actual_hash == hash
                if not verified:
                    print(
                        f"Got wrong checksum downloading {package} from {url}, "
                        f"download hash: {actual_hash}"
                    )
            elif package.size:
                print("No hash specified, checking file size instead.")
                actual_size = getsize(target_file)
                verified = actual_size == package.size
                if not verified:
                    print(
                        f"Got wrong filesize downloading {package} from {url}, "
                        f"download_size={actual_size}"
                    )
            else:
                print(
                    "WARN: No verification method available for package!\n"
                    f"Verification skipped for {target_file}"
                )
                verified = True

            if not verified:
                print(f"File {target_file} will now be removed.")
                remove(target_file)
                continue

            downloaded = True
            break

        if not downloaded:
            raise Exception(f"Could not download {package} from any of specified URLs")


if __name__ == "__main__":
    download_packages()
