import importlib
import os
import time


class Timer:
    def __init__(self):
        self.elapsed = float("nan")

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        if value is None:
            self.elapsed = time.perf_counter() - self._start


def get_benchmark_module(file_path):
    base_path = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.relpath(file_path, base_path)
    import_path = ".".join(os.path.split(module_path))
    bm_module = importlib.import_module(import_path)
    return bm_module, import_path
