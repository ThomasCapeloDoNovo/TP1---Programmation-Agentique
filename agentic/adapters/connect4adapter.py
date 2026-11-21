from .baseadapter import GameAdapter
from games.connectfour import ConnectFour
from pydantic import BaseModel

from agentic.schemas import Connect4State

class Connect4Adapter(GameAdapter):
    """
    Adaptation du Puissance 4 pour le moteur générique.
    """

    name = "connect4"

    def create_game(self):
        return ConnectFour()

    def parse_move(
        self,
        row: int | None,
        col: int | None,
    ):
        """
        Au Puissance 4 seule la colonne compte.

        La gravité du jeu détermine automatiquement la ligne finale du pion.
        """

        if col is None:
            raise ValueError("Pour le puissance 4, il faut 'col' (numéro de colonne, à partir de 1).")
        elif col < 1 or col > 7:
            raise ValueError("Pour le puissance, il faut que la valeur de 'col' soit comprise entre 1 et 7.")


        return col - 1

    def format_move(self, move):
        """
        Action native -> texte compréhensible.
        """

        return f"colonne {move + 1}"

    def build_state(self, state):
        return Connect4State(
            grid=[list(row) for row in state]
        )