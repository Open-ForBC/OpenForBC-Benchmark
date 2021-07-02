import os



def isBenchmark(path):
    try:
        if "benchmark_info.json" in os.listdir(path) and os.path.isdir(path):
            return True
    except NotADirectoryError:
        return False
    return False



class EmptyBenchmarkList(BaseException):
    def __str__(self):
        return "Please select benchmark(s) to run by pressing spacebar to select."
