from typing import Literal

from agentic.schemas import TicTacToeState
from .baserenderer import Renderer


class TicTacToeRenderer(Renderer):
    """
    Génère différentes représentations du Morpion.
    """

    SYMBOLS = {
        0: ".",
        1: "X",
        2: "O",
    }

    def render(
        self,
        state: TicTacToeState,
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
        state: TicTacToeState,
    ) -> str:
        """
        Affichage texte du plateau.
        """

        rows = [
            "  1 2 3"
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
        state: TicTacToeState,
    ):
        """
        TODO :
        retourner une image PNG/base64 du plateau.
        """

        raise NotImplementedError(
            "Le rendu image n'est pas encore implémenté."
        )