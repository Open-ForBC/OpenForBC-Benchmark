import importlib
import os
import math
from .benchmark_wrapper import BenchmarkWrapper
import pathlib


class BenchmarkFactory:
    def __init__(self) -> None:
        pass

    def getBenchmarkModule(self, file_path):
        base_path = pathlib.Path.cwd()
        module_path = os.path.relpath(file_path, base_path)
        import_path = ".".join(os.path.split(module_path))
        try:
            self.backend_module = importlib.import_module(import_path)
            return self.backend_module
        except ImportError as e:
            return f"{e}:Benchmark doesn't exist."


def estimate_repetitions(func, args=(), target_time=10, powers_of=10):
    # call function once for warm-up
    func(*args)

    # call again and measure time
    with BenchmarkWrapper.Timer() as t:
        func(*args)

    time_per_rep = t.elapsed
    exponent = math.log(target_time / time_per_rep, powers_of)
    num_reps = int(powers_of ** round(exponent))
    return max(powers_of, num_reps)
