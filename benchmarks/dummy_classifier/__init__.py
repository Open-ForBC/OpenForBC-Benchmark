import importlib
import functools
import json
from ..common.benchmark_factory import estimate_repetitions


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
        _runner = functools.partial(obj.startBenchmark)
        return _runner, estimate_repetitions(_runner)
    except TypeError:
        pass


def isStandAlone():
    with open("benchmarks/dummy_classifier/settings/settings1.json") as f:
        _ans = json.load(f)
        if _ans["stand-alone"] == "True":
            return [True, None]
        else:
            return [False, _ans["parent"]]


def hasBurnin():  # TODO: reduce number of times file is opened
    with open("benchmarks/dummy_classifier/settings/settings1.json") as f:
        try:
            return json.load(f)["burnin"]
        except:
            return 0
