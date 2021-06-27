import importlib
import functools


def try_import(bench="classifier"):
    try:
        return importlib.import_module(f".dummy_{bench}", __name__)
    except ImportError:
        return "not correct"


def get_callable(bench):
    backend_module = try_import(bench)
    return functools.partial(backend_module.run)
