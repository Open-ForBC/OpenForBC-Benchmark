import importlib
import functools


def tryImport():
    try:
        return importlib.import_module(f".implementation", __name__)
    except ImportError:
        return None


def getCallable():
    backend_module = tryImport()
    try:
        cls = getattr(backend_module, "DummyClassifier")  # class-name
    except (ImportError, AttributeError):
        raise ValueError(f"Unknown format {format!r}") from None
    obj = cls()
    try:
        return functools.partial(obj.startBenchmark)
    except TypeError:
        pass
