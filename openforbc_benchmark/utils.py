from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Iterable, List, Optional


from os import environ
from shlex import quote
from typing import TypedDict


class PopenArgs(TypedDict):
    args: "List[str]"
    cwd: "Optional[str]"
    env: "Optional[Dict[str, str]]"


class Runnable:
    """
    A runnable command.

    Contains command arguments and environment data, such as the current working
    directory, environment variables and additional PATH entries.
    """

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

    def __repr__(self) -> str:
        venv = False

        if self.env and "VIRTUAL_ENV" in self.env:
            venv = True
            virtualenv_path = self.env["VIRTUAL_ENV"]

        env = (
            None
            if self.env is None
            else " ".join(
                f"{quote(k)}={quote(v)}"
                for k, v in self.env.items()
                if k != "VIRTUAL_ENV"
            )
        )
        clean_path = [x for x in self.path if (not venv) or virtualenv_path not in x]
        path = None if not clean_path else f"PATH+={quote(':'.join(clean_path))}"
        return (
            f"{'(venv) ' if venv else ''}$ {path + ' ' if path else ''}"
            f"{env + ' ' if env else ''}{self.command_str()}"
        )

    def command_str(self) -> str:
        """Return the contatenated args."""
        return argv_join(self.args)

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
    """
    Return a shell-escaped string from *argv*.

    Backported for python3.6 from `shlex.join`.
    """
    return " ".join(quote(x) for x in argv)
