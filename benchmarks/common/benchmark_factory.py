import importlib
import os
import pathlib
from typing import List


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
