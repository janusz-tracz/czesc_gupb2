from abc import abstractmethod
from typing import Protocol

from gupb2.model import characters


class Controller(Protocol):

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def decide(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def preferred_tabard(self):
        raise NotImplementedError
