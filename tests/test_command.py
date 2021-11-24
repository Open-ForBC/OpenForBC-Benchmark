from openforbc_benchmark.common import Command


def test_command() -> None:
    command = Command("/bin/true")
    assert isinstance(command, Command)


def test_command_deserialize() -> None:
    assert isinstance(Command.deserialize("/bin/echo Hello"), Command)
    assert isinstance(
        Command.deserialize({"command": "/bin/true", "env": {"GPU": "CUDA"}}), Command
    )
    assert isinstance(
        Command.deserialize(
            {"command": ["echo", "hello world"], "env": {"GPU": "CUDA"}}
        ),
        Command,
    )
    assert isinstance(
        Command.deserialize(
            {
                "command": ["echo", "hello world"],
                "env": {"GPU": "CUDA"},
                "workdir": "presets/gpu",
            }
        ),
        Command,
    )
