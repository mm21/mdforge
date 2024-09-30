"""
Base element functionality.
"""

from abc import ABC, abstractmethod
from typing import Generator


class BaseElement(ABC):

    @abstractmethod
    def render(self) -> Generator[str, None, None]: ...
