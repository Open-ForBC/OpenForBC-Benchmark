from os.path import dirname, join, pardir

from openforbc_benchmark.benchmark import BenchmarkRun, BenchmarkSuite
from openforbc_benchmark.json import BenchmarkRunDefinition, BenchmarkSuiteDefinition

O4BC_BENCH_DIR = join(dirname(__file__), pardir)


def test_benchmark_suite_from_definition() -> None:
    suite = BenchmarkSuite.from_definition(
        BenchmarkSuiteDefinition(
            "Test suite",
            "",
            [BenchmarkRunDefinition("dummy_benchmark", ["preset1", "preset2"])],
        ),
        search_path=O4BC_BENCH_DIR,
    )

    assert isinstance(suite, BenchmarkSuite)
    assert suite.benchmark_runs[0].benchmark.name == "Dummy Benchmark"
    assert suite.benchmark_runs[0].presets[0].name == "preset1"
    assert suite.benchmark_runs[0].presets[1].name == "preset2"


def test_benchmark_run_from_definition() -> None:
    bench_run = BenchmarkRun.from_definition(
        BenchmarkRunDefinition("dummy_benchmark", ["preset1", "preset2"]),
        search_path=O4BC_BENCH_DIR,
    )

    assert isinstance(bench_run, BenchmarkRun)
    assert bench_run.benchmark.name == "Dummy Benchmark"
    assert bench_run.presets[0].name == "preset1"
    assert bench_run.presets[1].name == "preset2"
