import git
import os
import glob
from xml.dom import minidom
import urllib.request
import hashlib
from shutil import copy2 as cp
import stat
from sys import platform
import subprocess
from select import select
from contextlib import contextmanager
import json
import fileinput
import progressbar

REMOTE_BENCH_ROOT_PATH = os.path.join("ob-cache", "test-profiles", "pts")
file_dir = os.path.dirname(os.path.abspath(__file__))
clone_dir = os.path.join(file_dir, "phoronix-benchs")
bench_root_path = os.path.join(clone_dir, REMOTE_BENCH_ROOT_PATH)
o4bc_benchmark_dir = os.path.join(os.path.dirname(file_dir), "benchmarks")
implementation_template = os.path.join(file_dir, "phoronix_implementation.py.template")
benchmark_info_template = os.path.join(file_dir, "phoronix_benchmark_info.json.template")

installer_map = {"linux": "install.sh",
                 "linux2": "install.sh",
                 "darwin": "install_macosx.sh",
                 "windows": "install_windows.sh"}
bench_dict = {}


class ProgressBar():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar=progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()


@contextmanager
def pipe():
    r, w = os.pipe()
    yield r, w
    os.close(r)
    os.close(w)


def generate_dict():
    for bench in sorted(os.listdir(bench_root_path)):
        bench_name, bench_v = bench.rsplit('-', 1)

        if bench_name in bench_dict:
            bench_dict[bench_name].append(bench_v)
        else:
            bench_dict[bench_name] = [bench_v]


def phoronix_init():
    if not os.path.isdir(clone_dir):
        os.mkdir(clone_dir)

    repo = git.Repo.init(clone_dir)

    try:
        repo.create_remote("origin", "https://github.com/phoronix-test-suite/phoronix-test-suite")
    except git.exc.GitCommandError:
        print("Origin already set up.")

    repo.config_writer().set_value("core", "sparsecheckout", "true").release()

    sparse_checkout_info_file_path = os.path.join(clone_dir, ".git", "info", "sparse-checkout")

    if os.path.isfile(sparse_checkout_info_file_path):
        sparse_checkout_info_file = open(sparse_checkout_info_file_path, "w")
    else:
        sparse_checkout_info_file = open(sparse_checkout_info_file_path, "x")
    sparse_checkout_info_file.write(REMOTE_BENCH_ROOT_PATH)
    sparse_checkout_info_file.close()

    rebase = False
    try:
        repo.git.reset('--hard', 'origin/master')
        rebase = True
    except Exception:
        print("Nothing to reset")

    repo.remotes.origin.pull("master", rebase=rebase)


def phoronix_list(benchmark_name=None):
    if benchmark_name is None or not benchmark_name:
        if not bench_dict:
            generate_dict()
        for bench_name, bench_v in bench_dict.items():
            print("{} @ {}".format(bench_name, ', '.join(bench_v)))
    else:
        local_benchmark_repo = os.path.join(clone_dir, REMOTE_BENCH_ROOT_PATH, benchmark_name)
        results = glob.glob(os.path.join(bench_root_path, local_benchmark_repo + "*"))
        if results:
            if not bench_dict:
                generate_dict()
            print("{} @ {}".format(benchmark_name, ', '.join(bench_dict[benchmark_name])))
        else:
            raise Exception("Benchmark {} not found.".format(benchmark_name))
    pass


def phoronix_exists(benchmark_name, benchmark_v=None):
    if benchmark_name:
        if not bench_dict:
            generate_dict()
        if benchmark_name in bench_dict:
            if benchmark_v:
                return benchmark_v in bench_dict[benchmark_name]
            else:
                return True
        else:
            raise Exception("Benchmark name not valid.")
    else:
        raise Exception("Please provide a non-empty benchmark name.")


def phoronix_install(benchmark_name, benchmark_v=None): # noqa: C901
    if phoronix_exists(benchmark_name, benchmark_v):
        if not benchmark_v:
            benchmark_v = bench_dict[benchmark_name][-1]
        bench_path = os.path.join(bench_root_path, "{}-{}".format(benchmark_name, benchmark_v))

        downloads_xml_path = os.path.join(bench_path, "downloads.xml")
        downloads_xml = minidom.parse(downloads_xml_path)
        packages_list = downloads_xml.getElementsByTagName('Package')

        test_definition_xml_path = os.path.join(bench_path, "test-definition.xml")
        test_definition_xml = minidom.parse(test_definition_xml_path)
        info_section = test_definition_xml.getElementsByTagName('TestInformation')[0]
        info_benchmark_name = info_section.getElementsByTagName('Title')[0].firstChild.nodeValue
        info_benchmark_description = info_section.getElementsByTagName('Description')[0].firstChild.nodeValue

        settings_list = test_definition_xml.getElementsByTagName('Entry')

        target_dir = os.path.join(o4bc_benchmark_dir, 'phoronix-{}-{}'.format(benchmark_name, benchmark_v))

        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)

        settings_dir = os.path.join(target_dir, "settings")
        if not os.path.isdir(settings_dir):
            os.mkdir(settings_dir)

        default_settings_file = ''
        save_default_settings = True

        for setting in settings_list:
            name = setting.getElementsByTagName('Name')[0].firstChild.nodeValue.lower()
            cli_args = setting.getElementsByTagName('Value')[0].firstChild.nodeValue
            dict = {"cli_args": cli_args}
            with open(os.path.join(settings_dir, f"settings-{name}.json"), 'w+') as outfile:
                json.dump(dict, outfile)
                if save_default_settings:
                    default_settings_file = f"settings-{name}.json"
                    save_default_settings = False

        for installer in glob.glob(os.path.join(bench_path, "install*.sh")):
            cp(installer, target_dir)
            installer_path = os.path.join(target_dir, installer)
            os.chmod(installer_path, os.stat(installer_path).st_mode | stat.S_IEXEC)

        target_implementation_file = os.path.join(target_dir, "implementation.py")
        cp(implementation_template, target_implementation_file)
        benchmark_command = benchmark_name
        with open(os.path.join(bench_path, installer_map[platform])) as f:
            for line in f.readlines():
                if "chmod +x" in line:
                    benchmark_command = line.replace("chmod +x", '').rstrip().lstrip()
                    print("Executable found in {} as {}".format(installer_map[platform], benchmark_command))
        with fileinput.FileInput(target_implementation_file, inplace=True) as file:
            for line in file:
                print(line.replace("PUT_COMMAND_HERE", f"./{benchmark_command}"), end='')

        target_benchmark_info_file = os.path.join(target_dir, "benchmark_info.json")
        cp(benchmark_info_template, target_benchmark_info_file)
        with fileinput.FileInput(target_benchmark_info_file, inplace=True) as file:
            for line in file:
                print(line.replace("PUT_NAME_HERE", info_benchmark_name), end='')
        with fileinput.FileInput(target_benchmark_info_file, inplace=True) as file:
            for line in file:
                print(line.replace("PUT_DESCRIPTION_HERE", info_benchmark_description), end='')
        with fileinput.FileInput(target_benchmark_info_file, inplace=True) as file:
            for line in file:
                print(line.replace("PUT_DEFAULT_SETTINGS_HERE", default_settings_file), end='')

        for package in packages_list:
            urls = package.getElementsByTagName('URL')[0].firstChild.nodeValue.split(',')

            filename = package.getElementsByTagName('FileName')[0].firstChild.nodeValue

            try:
                md5 = package.getElementsByTagName('MD5')[0].firstChild.nodeValue
                print("Downloading {} (md5:{})".format(filename, md5))
            except Exception:
                md5 = None

                try:
                    sha256 = package.getElementsByTagName('SHA256')[0].firstChild.nodeValue
                    print("Downloading {} (sha256:{})".format(filename, sha256))
                except Exception:
                    sha256 = None

                    try:
                        size = package.getElementsByTagName('FileSize')[0].firstChild.nodeValue
                        print("Downloading {} (size:{})".format(filename, size))
                    except Exception:
                        size = None

            target_file = os.path.join(target_dir, filename)
            should_download = True

            if os.path.isfile(target_file):
                with open(target_file, 'rb') as f:
                    if md5:
                        if hashlib.md5(f.read()).hexdigest() == md5:
                            print("Already downloaded. Skipping.")
                            should_download = False
                    elif sha256:
                        if hashlib.sha256(f.read()).hexdigest() == sha256:
                            print("Already downloaded. Skipping.")
                            should_download = False
                    elif size:
                        if os.path.getsize(target_file) == size:
                            print("Already downloaded. Skipping.")
                            should_download = False
                    else:
                        os.remove(target_file)

            if should_download:
                for url in urls:
                    print(url)
                    try:
                        urllib.request.urlretrieve(url, target_file, ProgressBar())
                        verified = False
                        if md5:
                            if hashlib.md5(open(target_file, 'rb').read()).hexdigest() == md5:
                                verified = True
                        elif sha256:
                            if hashlib.sha256(open(target_file, 'rb').read()).hexdigest() == sha256:
                                verified = True
                        elif size:
                            if os.path.getsize(target_file) == size:
                                verified = True
                        else:
                            verified = False

                        if verified:
                            break
                        else:
                            print("Wrong checksum. Trying again.")
                            os.remove(target_file)
                    except Exception:
                        if url == urls[-1]:
                            raise Exception("None of the provided URLs works.")

        if os.path.isfile(os.path.join(target_dir, installer_map[platform])):
            cmd = ["bash", installer_map[platform]]
            my_env = os.environ.copy()
            my_env["HOME"] = target_dir

            # from https://gist.github.com/phizaz/e81d3d362e89bc68055cfcd670d44e9b
            with pipe() as (r, w):
                with subprocess.Popen(cmd, stdout=w, stderr=w, cwd=target_dir, env=my_env) as p:
                    while p.poll() is None:
                        while len(select([r], [], [], 0)[0]) > 0:
                            buf = os.read(r, 1024)
                            print(buf.decode('utf-8'), end='')
        else:
            raise Exception(f"The current platform ({platform}) is not supported by this benchmark.")
    else:
        raise Exception(f"The required benchmark {benchmark_name} @ {benchmark_v} doesn't exist.")


if __name__ == "__main__":
    # print("Listing all benchmarks:")
    # phoronix_list("")

    # print()
    # print("Listing all vpxenc versions:")
    # phoronix_list("vpxenc")

    # print()
    # print("Trying to list non-existing benchmark:")
    # phoronix_list("doesnt_exists")

    # print()
    # print("Checking x11perf benchmark existance:")
    # print(phoronix_exists("x11perf"))

    # print()
    # print("Checking php 1.0.0 benchmark existance:")
    # print(phoronix_exists("php", "1.0.0"))

    # print()
    # print("Checking php 5.0.0 benchmark existance:")
    # print(phoronix_exists("php", "5.0.0"))

    # print()
    # print("Checking doesnt_exists benchmark existance:")
    # print(phoronix_exists("doesnt_exists"))

    # print()
    # print("Checking doesnt_exists benchmark existance:")
    # print(phoronix_exists("doesnt_exists", "1.0.0"))

    phoronix_init()
    # phoronix_install("astcenc", "1.1.0")
