from openforbc_benchmark.json import (
    BenchmarkDefinition,
    BenchmarkSuiteDefinition,
    CommandInfo,
    PresetDefinition,
)


def test_benchmark_serialization() -> None:
    benchmark = BenchmarkDefinition(
        "name",
        "desc",
        None,
        [CommandInfo("echo Hello world")],
        None,
        CommandInfo("echo {}"),
        False,
    )
    assert isinstance(benchmark, BenchmarkDefinition)


def test_benchmark_deserialization() -> None:
    from json import loads

    json = r"""
    {
        "name": "Dummy Benchmark",
        "description": "Prints something to the output",
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


def test_benchmark_preset() -> None:
    preset = PresetDefinition(
        "--config=gpu_48x48.json", [CommandInfo("init.sh --preset=gpu_48x48.json")]
    )
    assert isinstance(preset, PresetDefinition)


def test_benchmark_preset_deserialization() -> None:
    from json import loads

    json = r"""
    {
        "args": "--config=preset_57.conf",
        "init_command": "setup_preset.sh preset_57.conf",
        "post_command": "setup_preset.sh --teardown"
    }
    """
    preset = PresetDefinition.deserialize(loads(json))
    assert isinstance(preset, PresetDefinition)


def test_benchmark_suite_deserialization() -> None:
    from json import loads

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
    assert benchmark_suite.benchmark_runs[0].benchmark_id == "dummy_bench"
    assert benchmark_suite.benchmark_runs[0].presets == ["preset1", "preset2"]


def test_command() -> None:
    command = CommandInfo("/bin/true")
    assert isinstance(command, CommandInfo)


def test_command_deserialize() -> None:
    assert isinstance(CommandInfo.deserialize("/bin/echo Hello"), CommandInfo)
    assert isinstance(
        CommandInfo.deserialize({"command": "/bin/true", "env": {"GPU": "CUDA"}}),
        CommandInfo,
    )
    assert isinstance(
        CommandInfo.deserialize(
            {"command": ["echo", "hello world"], "env": {"GPU": "CUDA"}}
        ),
        CommandInfo,
    )
    assert isinstance(
        CommandInfo.deserialize(
            {
                "command": ["echo", "hello world"],
                "env": {"GPU": "CUDA"},
                "workdir": "presets/gpu",
            }
        ),
        CommandInfo,
    )
