from .baseadapter import GameAdapter
from games.tictactoe import TicTacToe
from pydantic import BaseModel

from agentic.schemas import TicTacToeState
    
class TicTacToeAdapter(GameAdapter):
    """
    Adaptation du Morpion pour le moteur générique.
    """

    name = "tictactoe"

    def create_game(self):
        return TicTacToe()

    def parse_move(
        self,
        row: int | None,
        col: int | None,
    ):
        """
        Le morpion nécessite une ligne ET une colonne.

        Les coordonnées reçues sont en base 1
        (plus naturel pour l'utilisateur).

        Elles sont converties en base 0 pour le moteur.
        """

        if row is None or col is None:
            raise ValueError("Pour le tictactoe, il faut 'row' ET 'col' (de 1 à 3).")
        if row is not None and (row < 1 or row > 3):
            raise ValueError("Pour le tictactoe, il faut que la valeur de 'row' soit comprise entre 1 et 3.")
        if col is not None and (col < 1 or col > 3):
            raise ValueError("Pour le tictactoe, il faut que la valeur de 'col' soit comprise entre 1 et 3.")
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
        return TicTacToeState(
            grid=[list(row) for row in state]
        )