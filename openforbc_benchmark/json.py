"""JSON module contains classes used for JSON (de)serialization."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class Serializable(ABC):
    """
    A Serializable class can be serialized/deserialized into/from a JSON document.

    This abstract class provides methods to read/write such objects from/into a file.
    """

    @classmethod
    def serialize(cls, obj: Any) -> Any:
        """Serialize `obj` into a JSON object."""
        return obj.__dict__

    @classmethod
    @abstractmethod
    def deserialize(cls, json: Any) -> Serializable:
        """Deserialize instance from a JSON object."""
        pass

    def to_file(self, filename: str) -> None:
        """Serialize object as JSON into a file."""
        from json import dump

        with open(filename, "w") as file:
            dump(
                self.__class__.serialize(self),
                file,
                default=self.__class__.serialize,
            )

    @classmethod
    def from_file(cls, filename: str) -> Serializable:
        """Deserialize object as JSON from a file."""
        from json import load

        with open(filename, "r") as file:
            return cls.deserialize(load(file))
