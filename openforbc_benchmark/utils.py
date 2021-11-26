from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional


from dataclasses import dataclass, field
from os import environ
from typing_extensions import TypedDict


class PopenArgs(TypedDict):
    args: list[str]
    cwd: Optional[str]
    env: Optional[dict[str, str]]


@dataclass
class Runnable:
    """A process which can be run."""

    args: list[str]
    cwd: Optional[str] = None
    env: Optional[dict[str, str]] = None
    path: list[str] = field(default_factory=list)

    def into_popen_args(self, env: dict[str, str] = environ.copy()) -> PopenArgs:
        """Transform into subprocess.Popen init args."""
        from os.path import abspath

        if self.path:
            env.update(
                {
                    "PATH": ":".join(map(lambda x: abspath(x), self.path))
                    + ":"
                    + env["PATH"]
                }
            )

        if self.env is not None:
            env.update(self.env)

        return {
            "args": self.args,
            "cwd": self.cwd,
            "env": env if self.path or self.env is not None else None,
        }
