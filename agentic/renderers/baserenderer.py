# renderers/base.py

from abc import ABC, abstractmethod
from typing import Literal

class Renderer(ABC):
    """
    Transforme un état de jeu en représentation.

    Un même renderer peut produire plusieurs formats
    à partir du même état.
    """

    @abstractmethod
    def render(
        self,
        state,
        format: Literal["text", "image"],
    ):
        pass
