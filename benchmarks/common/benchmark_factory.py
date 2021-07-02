import importlib
import os
import math
import time
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
    with Timer() as t:
        func(*args)

    time_per_rep = t.elapsed
    exponent = math.log(target_time / time_per_rep, powers_of)
    num_reps = int(powers_of ** round(exponent))
    return max(powers_of, num_reps)


# class SetupContext:
#     def __init__(self, f):
#         self._f = f
#         self._f_args = (tuple(), dict())

#     def __call__(self, *args, **kwargs):
#         self._f_args = (args, kwargs)
#         return self

#     def __enter__(self):
#         self._env = os.environ.copy()
#         args, kwargs = self._f_args
#         self._f_iter = iter(self._f(*args, **kwargs))

#         try:
#             next(self._f_iter)
#         except Exception as e:
#             raise BackendNotSupported(str(e)) from None

#         return self

#     def __exit__(self, *args, **kwargs):
#         try:
#             next(self._f_iter)
#         except StopIteration:
#             pass
#         os.environ = self._env


# setup_function = SetupContext