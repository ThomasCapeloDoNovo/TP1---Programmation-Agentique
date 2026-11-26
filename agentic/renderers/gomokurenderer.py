from typing import Literal

from agentic.schemas import GomokuState
from .baserenderer import Renderer


class GomokuRenderer(Renderer):
    """
    Génère différentes représentations du Gomoku.
    """

    SYMBOLS = {
        0: ".",
        1: "X",
        2: "O",
    }

    def render(
        self,
        state: GomokuState,
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
        state: GomokuState,
    ) -> str:
        """
        Affichage texte du plateau.
        """

        rows = ["  " + " ".join(str(c + 1) for c in range(len(state.grid[0])))]

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
        state: GomokuState,
    ):
        """
        TODO :
        retourner une image PNG/base64 du plateau.
        """

        raise NotImplementedError(
            "Le rendu image n'est pas encore implémenté."
        )