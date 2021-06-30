import os


def isBenchmark(path):
    try:
        if "benchmark_info.json" in os.listdir(path) and os.path.isdir(path):
            return True
    except NotADirectoryError:
        return False
    return False
