import importlib
from ..common.benchmark_factory import estimate_repetitions


def tryImport():
    try:
        return importlib.import_module(f".implementation", __name__)
    except ImportError:
        return None


def getClass():
    backend_module = tryImport()
    try:
        cls = getattr(backend_module, "DummyClassifier")  # class-name
    except (ImportError, AttributeError):
        raise ValueError(f"Unknown format {format!r}") from None
    obj = cls()
    return obj
