from os.path import dirname, join, pardir

from openforbc_benchmark.benchmark import (
    Benchmark,
    BenchmarkRun,
    BenchmarkSuite,
    Preset,
    find_benchmark,
    get_benchmarks,
)
from openforbc_benchmark.json import (
    BenchmarkDefinition,
    BenchmarkRunDefinition,
    BenchmarkSuiteDefinition,
    CommandInfo,
    StatMatchInfo,
)

O4BC_BENCH_DIR = join(dirname(__file__), pardir)


def get_dummy_benchmark() -> Benchmark:
    return Benchmark.from_definition_file(
        join(O4BC_BENCH_DIR, "benchmarks", "dummy_benchmark", "benchmark.json")
    )


def get_dummy_py_benchmark() -> Benchmark:
    return Benchmark.from_definition_file(
        join(O4BC_BENCH_DIR, "benchmarks", "dummy_py_benchmark", "benchmark.json")
    )


def get_dummy_run() -> BenchmarkRun:
    return BenchmarkRun(
        get_dummy_benchmark(), [get_dummy_benchmark().get_default_preset()]
    )


def get_dummy_py_run() -> BenchmarkRun:
    return BenchmarkRun(
        get_dummy_py_benchmark(), [get_dummy_py_benchmark().get_default_preset()]
    )


def test_benchmark_from_definition() -> None:
    benchmark = Benchmark.from_definition(
        BenchmarkDefinition(
            "Name",
            "description",
            "preset",
            None,
            [CommandInfo("echo hello")],
            None,
            [CommandInfo("true")],
            {"stat_1": StatMatchInfo("dummy_regex")},
            False,
        ),
        "dummy_dir",
    )
    assert isinstance(benchmark, Benchmark)
    assert benchmark.name == "Name"
    assert benchmark.description == "description"
    assert benchmark.default_preset == "preset"
    assert benchmark.run_commands[0].command == ["echo", "hello"]
    assert benchmark.test_commands[0].command == ["true"]
    assert isinstance(benchmark.stats, dict)
    assert benchmark.stats["stat_1"].regex == "dummy_regex"
    assert not benchmark.virtualenv
    assert benchmark.dir == "dummy_dir"


def test_benchmark_from_definition_file() -> None:
    benchmark = get_dummy_benchmark()
    assert isinstance(benchmark, Benchmark)
    assert benchmark.name == "Dummy Benchmark"
    assert benchmark.description == "Does nothing"
    assert benchmark.run_commands[0].command == ["echo", "data:", "135246"]
    assert benchmark.setup_commands is not None
    assert benchmark.setup_commands[0].command == ["echo", "hello world"]
    assert benchmark.setup_commands[0].env == {
        "INSTALL": "1",
        "ENVIRONMENT": "production",
    }
    assert benchmark.setup_commands[0].workdir == "presets"
    assert benchmark.cleanup_commands is not None
    assert benchmark.cleanup_commands[0].command == ["echo", "daw"]
    assert isinstance(benchmark.stats, dict)
    assert benchmark.stats["data_1"].regex == r"data: (\d+)"
    assert not benchmark.virtualenv


def test_benchmark_get_presets() -> None:
    benchmark = get_dummy_benchmark()
    assert benchmark.get_presets()


def test_benchmark_get_default_preset() -> None:
    benchmark = get_dummy_benchmark()
    default = benchmark.get_default_preset()
    assert isinstance(default, Preset)
    assert default.name == "preset1"
    assert default.args == ["--config=preset1.conf"]


def test_benchmark_get_preset() -> None:
    benchmark = get_dummy_benchmark()
    preset = benchmark.get_preset("preset1")
    assert isinstance(preset, Preset)
    assert preset.name == "preset1"
    assert preset.args == ["--config=preset1.conf"]


def test_benchmark_run_setup() -> None:
    run = get_dummy_run()
    setup_tasks = list(run.setup())
    assert setup_tasks[0].args == ["echo", "hello world"]


def test_benchmark_run_py_setup() -> None:
    run = get_dummy_py_run()
    setup_tasks = list(run.setup())
    assert setup_tasks[0].args == ["python3", "-m", "venv", ".venv"]
    assert all(
        task.env is not None and "VIRTUAL_ENV" in task.env for task in setup_tasks[1:]
    )
    assert setup_tasks[1].args == ["echo", "hello world"]


def test_benchmark_run_run() -> None:
    run = get_dummy_run()
    assert list(run.setup())  # "run" setup tasks
    presets = list(run.run())
    assert presets[0][0].name == "preset1"
    tasks = list(presets[0][1])
    assert all(task.env is None or "VIRTUAL_ENV" not in task.env for task in tasks)
    assert tasks[0].args == ["echo", "setup.sh", "--config=preset1.conf"]
    assert tasks[1].args == ["echo", "data:", "135246", "--config=preset1.conf"]


def test_benchmark_run_py_run() -> None:
    run = get_dummy_py_run()
    assert list(run.setup())  # "run" setup tasks
    presets = list(run.run())
    assert presets[0][0].name == "preset1"
    tasks = list(presets[0][1])
    assert all(task.env is not None and "VIRTUAL_ENV" in task.env for task in tasks)
    assert tasks[0].args == ["echo", "setup.sh", "--config=preset1.conf"]
    assert tasks[1].args == ["echo", "data:", "135246", "--config=preset1.conf"]


def test_benchmark_run_cleanup() -> None:
    run = get_dummy_run()
    assert list(run.setup())  # "run" setup tasks
    tasks = list(run.cleanup())
    assert all(task.env is None or "VIRTUAL_ENV" not in task.env for task in tasks)
    assert tasks[0].args == ["echo", "daw"]


def test_benchmark_run_test() -> None:
    run = get_dummy_run()
    assert list(run.setup())  # "run" setup tasks
    tasks = list(run.test())
    assert tasks[0].args == ["true"]


def test_benchmark_run_py_test() -> None:
    run = get_dummy_py_run()
    assert list(run.setup())  # "run" setup tasks
    tasks = list(run.test())
    assert all(task.env is not None and "VIRTUAL_ENV" in task.env for task in tasks)
    print(tasks)
    assert tasks[0].args == ["true"]


def test_benchmark_run_py_cleanup() -> None:
    run = get_dummy_py_run()
    assert list(run.setup())  # "run" setup tasks
    tasks = list(run.cleanup())
    assert all(task.env is not None and "VIRTUAL_ENV" in task.env for task in tasks)
    assert tasks[0].args == ["echo", "daw"]


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


def test_get_benchmarks() -> None:
    benchmarks = get_benchmarks(O4BC_BENCH_DIR)
    assert benchmarks


def test_find_benchmark() -> None:
    benchmark = find_benchmark("dummy_benchmark", O4BC_BENCH_DIR)
    assert benchmark is not None
    assert benchmark.name == "Dummy Benchmark"
