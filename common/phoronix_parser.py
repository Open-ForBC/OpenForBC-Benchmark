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

REMOTE_BENCH_ROOT_PATH = os.path.join("ob-cache", "test-profiles", "pts")
file_dir = os.path.dirname(os.path.abspath(__file__))
clone_dir = os.path.join(file_dir, "phoronix-benchs")
bench_root_path = os.path.join(clone_dir, REMOTE_BENCH_ROOT_PATH)
o4bc_benchmark_dir = os.path.join(os.path.dirname(file_dir), "benchmarks")
bench_dict = {}


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
    repo.create_remote("origin", "https://github.com/phoronix-test-suite/phoronix-test-suite")
    repo.config_writer().set_value("core", "sparsecheckout", "true").release()

    sparse_checkout_info_file_path = os.path.join(clone_dir, ".git", "info", "sparse-checkout")

    if os.path.isfile(sparse_checkout_info_file_path):
        sparse_checkout_info_file = open(sparse_checkout_info_file_path, "w")
    else:
        sparse_checkout_info_file = open(sparse_checkout_info_file_path, "x")
    sparse_checkout_info_file.write(REMOTE_BENCH_ROOT_PATH)
    sparse_checkout_info_file.close()

    repo.remotes.origin.pull("master")


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


def phoronix_install(benchmark_name, benchmark_v=None):
    if phoronix_exists(benchmark_name, benchmark_v):
        if not benchmark_v:
            benchmark_v = bench_dict[benchmark_name][-1]
        bench_path = os.path.join(bench_root_path, "{}-{}".format(benchmark_name, benchmark_v))
        downloads_xml_path = os.path.join(bench_path, "downloads.xml")

        if os.path.isfile(downloads_xml_path):
            downloads_xml = minidom.parse(downloads_xml_path)
            packages_list = downloads_xml.getElementsByTagName('Package')
            target_dir = os.path.join(o4bc_benchmark_dir, 'phoronix-{}-{}'.format(benchmark_name, benchmark_v))

            if not os.path.isdir(target_dir):
                os.mkdir(target_dir)

            for installer in glob.glob(os.path.join(bench_path, "install*.sh")):
                cp(installer, target_dir)
                installer_path = os.path.join(target_dir, installer)
                os.chmod(installer_path, os.stat(installer_path).st_mode | stat.S_IEXEC)

            for package in packages_list:
                urls = package.getElementsByTagName('URL')[0].firstChild.nodeValue.split(',')
                md5 = package.getElementsByTagName('MD5')[0].firstChild.nodeValue
                # sha256 = package.getElementsByTagName('SHA256')[0].firstChild.nodeValue
                filename = package.getElementsByTagName('FileName')[0].firstChild.nodeValue
                # size = package.getElementsByTagName('FileSize')[0].firstChild.nodeValue
                print("Downloading {} (md5:{})".format(filename, md5))
                target_file = os.path.join(target_dir, filename)
                should_download = True

                if os.path.isfile(target_file):
                    if hashlib.md5(open(target_file, 'rb').read()).hexdigest() == md5:
                        print("Already downloaded. Skipping.")
                        should_download = False
                    else:
                        os.remove(target_file)

                if should_download:
                    for url in urls:
                        print(url)
                        try:
                            urllib.request.urlretrieve(url, filename=target_file)
                            if hashlib.md5(open(target_file, 'rb').read()).hexdigest() == md5:
                                break
                            else:
                                print("Wrong checksum. Trying again.")
                                os.remove(target_file)
                        except Exception:
                            if not url == urls[-1]:
                                print("Trying another url")
                                pass
                            else:
                                raise Exception("None of the provided URLs works.")

            cmd = ("bash").split(' ')

            if platform == "linux" or platform == "linux2":
                cmd.append("install.sh")
            elif platform == "darwin":
                cmd.append("install_macosx.sh")
            elif platform == "win32":
                cmd.append("install_windows.sh")

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=target_dir)
            output, error = process.communicate()
            print(output.decode('utf-8'))

    else:
        raise Exception("downloads.xml not found for {} benchmark.".format(benchmark_name))


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

    phoronix_install("astcenc", "1.1.0")
