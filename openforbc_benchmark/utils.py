from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Iterable, List, Optional


from os import environ
from typing_extensions import TypedDict


class PopenArgs(TypedDict):
    args: "List[str]"
    cwd: "Optional[str]"
    env: "Optional[Dict[str, str]]"


class Runnable:
    """A process which can be run."""

    def __init__(
        self,
        args: "List[str]",
        cwd: "Optional[str]" = None,
        env: "Optional[Dict[str, str]]" = None,
        path: "List[str]" = [],
    ) -> None:
        self.args = args
        self.cwd = cwd
        self.env = env
        self.path = path

    def into_popen_args(self, env: "Dict[str, str]" = environ.copy()) -> PopenArgs:
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


def argv_join(argv: "Iterable[str]") -> str:
    from shlex import quote

    return " ".join(quote(x) for x in argv)
