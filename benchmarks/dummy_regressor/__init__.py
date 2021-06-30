import importlib
import functools


def tryImport():
    try:
        return importlib.import_module(f".implementation", __name__)
    except ImportError:
        return None


def getCallable():
    backend_module = tryImport()
    cls = getattr(backend_module, "DummyRegressor")  # class name
    obj = cls()
    try:
        return functools.partial(obj.startBenchmark)
    except TypeError:
        pass
