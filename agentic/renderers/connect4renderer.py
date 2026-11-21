from typing import Literal

from agentic.schemas import Connect4State
from .baserenderer import Renderer


class Connect4Renderer(Renderer):
    """
    Génère différentes représentations du Puissance 4.
    """

    SYMBOLS = {
        0: ".",
        1: "X",
        2: "O",
    }

    def render(
        self,
        state: Connect4State,
        format: Literal["text", "image"],
    ):

        match format:

            case "text":
                return self._render_text(state)

            case "image":
                return self._render_image(state)

            case _:
                raise ValueError(
                    f"Format non supporté : {format}"
                )

    def _render_text(
        self,
        state: Connect4State,
    ) -> str:
        """
        Affichage texte du plateau.
        """

        rows = [
            "  1 2 3 4 5 6 7"
        ]

        for i, row in enumerate(state.grid):

            rows.append(
                f"{i + 1} "
                + " ".join(
                    self.SYMBOLS[cell]
                    for cell in row
                )
            )

        return "\n".join(rows)

    def _render_image(
        self,
        state: Connect4State,
    ):
        """
        TODO :
        retourner une image PNG/base64 du plateau.
        """

        raise NotImplementedError(
            "Le rendu image n'est pas encore implémenté."
        )
