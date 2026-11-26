from .baseadapter import GameAdapter
from games.gomoku import Gomoku
from pydantic import BaseModel

from agentic.schemas import GomokuState
    
class GomokuAdapter(GameAdapter):
    """
    Adaptation du Gomoku pour le moteur générique.
    """

    name = "gomoku"
    size = 7
    align = 5

    def create_game(self):
        return Gomoku(size=self.size, align=self.align)

    def parse_move(
        self,
        row: int | None,
        col: int | None,
    ):
        """
        Le gomoku nécessite une ligne ET une colonne.

        Les coordonnées reçues sont en base 1
        (plus naturel pour l'utilisateur).

        Elles sont converties en base 0 pour le moteur.
        """

        if row is None or col is None:
            raise ValueError(f"Pour le gomoku, il faut 'row' ET 'col' (de 1 à {self.size}).")
        if not 1 <= row <= self.size:
            raise ValueError(f"Pour le gomoku, il faut que la valeur de 'row' soit comprise entre 1 et {self.size}.")
        if not 1 <= col <= self.size:
            raise ValueError(f"Pour le gomoku, il faut que la valeur de 'col' soit comprise entre 1 et {self.size}.")
        return (row - 1, col - 1)

    def format_move(self, move):
        """
        Action native -> texte compréhensible.
        """

        return (
            f"ligne {move[0] + 1}, "
            f"colonne {move[1] + 1}"
        )
    
    def build_state(self, state):
        return GomokuState(
            grid=[list(row) for row in state]
        )