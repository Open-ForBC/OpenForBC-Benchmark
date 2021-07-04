from benchmarks.common.benchmark_factory import estimate_repetitions
import importlib
import functools

def tryImport():
    try:
        return importlib.import_module(f".dummy_suite", __name__)
    except ImportError:
        return None


def getCallable():
    backend_module = tryImport()
    try:
        cls = getattr(backend_module, "DummyBenchmarkSuite")  # class-name
        
    except (ImportError, AttributeError):
        raise ValueError(f"Unknown format {format!r}") from None
    obj = cls()
    return obj