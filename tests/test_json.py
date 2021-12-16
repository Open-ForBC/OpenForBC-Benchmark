from json import loads

from openforbc_benchmark.json import (
    BenchmarkDefinition,
    BenchmarkRunDefinition,
    BenchmarkStats,
    BenchmarkSuiteDefinition,
    CommandInfo,
    PresetDefinition,
    StatMatchInfo,
)


def test_benchmark_deserialization() -> None:
    json = r"""
    {
        "name": "Dummy Benchmark",
        "description": "Prints something to the output",
        "default_preset": "preset",
        "run_command": "echo Hello world!",
        "setup_command": {
            "command": "echo",
            "env": {
            "INSTALL": "1",
            "ENVIRONMENT": "production"
            },
            "workdir": "presets"
        },
        "cleanup_command": {
            "command": [
            "echo",
            "daw"
            ]
        },
        "stats": {
            "data_1": {
            "regex": "data: (\\d+)",
            "file": "test/output.log"
            }
        }
    }
    """
    benchmark = BenchmarkDefinition.deserialize(loads(json))
    assert isinstance(benchmark, BenchmarkDefinition)
    assert benchmark.name == "Dummy Benchmark"
    assert benchmark.description == "Prints something to the output"
    assert benchmark.run_commands[0].command == ["echo", "Hello", "world!"]
    assert benchmark.setup_commands is not None
    assert benchmark.setup_commands[0].command == ["echo"]
    assert benchmark.setup_commands[0].env["INSTALL"] == "1"
    assert benchmark.setup_commands[0].env["ENVIRONMENT"] == "production"
    assert benchmark.setup_commands[0].workdir == "presets"
    assert benchmark.cleanup_commands is not None
    assert benchmark.cleanup_commands[0].command == ["echo", "daw"]
    assert isinstance(benchmark.stats, dict)
    assert benchmark.stats["data_1"].regex == r"data: (\d+)"
    assert benchmark.stats["data_1"].file == "test/output.log"


def test_preset_deserialization() -> None:
    json = r"""
    {
        "args": "--config=preset_57.conf",
        "init_command": "setup_preset.sh preset_57.conf",
        "post_command": "setup_preset.sh --teardown"
    }
    """
    preset = PresetDefinition.deserialize(loads(json))
    assert isinstance(preset, PresetDefinition)
    assert preset.args == ["--config=preset_57.conf"]
    assert preset.init_commands is not None
    assert preset.init_commands[0].command == ["setup_preset.sh", "preset_57.conf"]
    assert preset.post_commands is not None
    assert preset.post_commands[0].command == ["setup_preset.sh", "--teardown"]


def test_benchmark_suite_deserialization() -> None:
    json = r"""
    {
    "name": "Sample suite",
    "description": "A sample benchmark suite",
    "benchmark_runs": [ {
        "benchmark_folder": "dummy_bench",
        "presets": [ "preset1", "preset2" ]
    } ]
    }
    """
    benchmark_suite = BenchmarkSuiteDefinition.deserialize(loads(json))
    assert isinstance(benchmark_suite, BenchmarkSuiteDefinition)
    assert benchmark_suite.name == "Sample suite"
    assert benchmark_suite.description == "A sample benchmark suite"
    assert benchmark_suite.benchmark_runs
    assert benchmark_suite.benchmark_runs[0].benchmark_folder == "dummy_bench"
    assert benchmark_suite.benchmark_runs[0].presets == ["preset1", "preset2"]


def test_command_deserialization() -> None:
    def_1 = "/bin/echo Hello world"
    cmd_1 = CommandInfo.deserialize(def_1)
    assert isinstance(cmd_1, CommandInfo)
    assert cmd_1.command == ["/bin/echo", "Hello", "world"]

    def_2 = r"""
    {
        "command": "/bin/true",
        "env": {
            "GPU": "CUDA"
        }
    }
    """
    cmd_2 = CommandInfo.deserialize(loads(def_2))
    assert isinstance(cmd_2, CommandInfo)
    assert cmd_2.command == ["/bin/true"]
    assert cmd_2.env == {"GPU": "CUDA"}

    def_3 = r"""
    {
        "command": ["echo", "hello world"],
        "env": { "GPU": "CUDA" },
        "workdir": "presets/gpu"
    }
    """
    cmd_3 = CommandInfo.deserialize(loads(def_3))
    assert isinstance(cmd_3, CommandInfo)
    assert cmd_3.command == ["echo", "hello world"]
    assert cmd_3.env == {"GPU": "CUDA"}
    assert cmd_3.workdir == "presets/gpu"


def test_stat_match_deserialization() -> None:
    json = r"""
    {
        "file": "output",
        "regex": "testregex ()"
    }
    """
    statmatch = StatMatchInfo.deserialize(loads(json))
    assert isinstance(statmatch, StatMatchInfo)
    assert statmatch.file == "output"
    assert statmatch.regex == "testregex ()"


def test_stats_deserialization() -> None:
    from jsonschema import ValidationError
    from pytest import raises

    valid_json = r"""
    {
        "data1": 123
    }
    """
    valid_stats = BenchmarkStats.deserialize(loads(valid_json))
    assert isinstance(valid_stats, BenchmarkStats)
    assert valid_stats.stats["data1"] == 123

    invalid_json_1 = r"""
    {
        "data2": "a string"
    }
    """
    with raises(ValidationError):
        BenchmarkStats.deserialize(invalid_json_1)

    invalid_json_2 = "{}"
    with raises(ValidationError):
        BenchmarkStats.deserialize(invalid_json_2)


def test_benchmark_run_definition() -> None:
    json = r"""
    {
        "benchmark_folder": "dummy",
        "presets": [ "preset1", "preset2" ]
    }
    """
    run = BenchmarkRunDefinition.deserialize(loads(json))
    assert isinstance(run, BenchmarkRunDefinition)
    assert run.benchmark_folder == "dummy"
    assert run.presets == ["preset1", "preset2"]
