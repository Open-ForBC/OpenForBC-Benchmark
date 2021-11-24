from openforbc_benchmark.common import Command
from openforbc_benchmark.benchmark import Benchmark, Preset


def test_benchmark_serialization() -> None:
    benchmark = Benchmark(
        "name",
        "desc",
        None,
        [Command("echo Hello world")],
        None,
        Command("echo {}"),
        False,
    )
    assert isinstance(benchmark, Benchmark)


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
    benchmark = Benchmark.deserialize(loads(json))
    assert isinstance(benchmark, Benchmark)


def test_benchmark_preset() -> None:
    preset = Preset(
        "--config=gpu_48x48.json", [Command("init.sh --preset=gpu_48x48.json")]
    )
    assert isinstance(preset, Preset)


def test_benchmark_preset_deserialization() -> None:
    from json import loads

    json = r"""
    {
        "args": "--config=preset_57.conf",
        "init_command": "setup_preset.sh preset_57.conf",
        "post_command": "setup_preset.sh --teardown"
    }
    """
    preset = Preset.deserialize(loads(json))
    assert isinstance(preset, Preset)
