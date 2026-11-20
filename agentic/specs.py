# agentic/specs.py
# Une "fiche" par jeu : comment traduire les arguments des outils (1-indexés,
# faciles pour un humain/LLM) en actions natives des classes (0-indexées).
from dataclasses import dataclass
from typing import Any, Callable

from games.tictactoe import TicTacToe
from games.connectfour import ConnectFour


#  Affichage générique d'une grille 
def render_grid(game, state) -> str:
    """Transforme un état (tuple de tuples) en texte. Marche pour tout jeu en grille."""
    blank = getattr(game, "blank", 0)
    sym = {blank: ".", game.player1: "X", game.player2: "O"}
    n_cols = len(state[0])
    header = "  " + " ".join(str(c + 1) for c in range(n_cols))      # numéros de colonnes 1..n
    rows = [f"{i + 1} " + " ".join(sym.get(cell, "?") for cell in row)
            for i, row in enumerate(state)]
    return "\n".join([header] + rows)


#  Traduction arguments -> action native 
def parse_ttt(row: int | None, col: int | None):
    # tictactoe : il faut les deux coordonnées. On convertit 1-indexé -> 0-indexé.
    if row is None or col is None:
        raise ValueError("Pour le tictactoe, il faut 'row' ET 'col' (de 1 à 3).")
    if row is not None and (row < 1 or row > 3):
        raise ValueError("Pour le tictactoe, il faut que la valeur de 'row' soit comprise entre 1 et 3.")
    if col is not None and (col < 1 or col > 3):
        raise ValueError("Pour le tictactoe, il faut que la valeur de 'col' soit comprise entre 1 et 3.")
    return (row - 1, col - 1)


def parse_c4(row: int | None, col: int | None):
    # connect 4 : seule la colonne compte (la gravité décide de la ligne).
    # l'action est un entier de colonne 0..6.
    if col is None:
        raise ValueError("Pour le puissance 4, il faut 'col' (numéro de colonne, à partir de 1).")
    elif col < 1 or col > 7:
        raise ValueError("Pour le puissance, il faut que la valeur de 'col' soit comprise entre 1 et 7.")

    return col - 1


#  Action native -> texte lisible 
def fmt_ttt(a): return f"ligne {a[0] + 1}, colonne {a[1] + 1}"
def fmt_c4(a):  return f"colonne {a + 1}"


@dataclass
class GameSpec:
    name: str
    make_game: Callable[[], Any]                 # construit une instance du jeu
    parse_move: Callable[[int | None, int | None], Any]
    format_move: Callable[[Any], str]
    ai_depth: int                                # profondeur max de Minimax pour ce jeu
    ai_time: float                               # temps max (s) par coup


# Registre : pour ajouter un jeu plus tard, on ajoute UNE ligne ici.
SPECS: dict[str, GameSpec] = {
    "tictactoe": GameSpec("tictactoe", TicTacToe, parse_ttt, fmt_ttt, ai_depth=9, ai_time=1.0),
    "connect4":  GameSpec("connect4",  ConnectFour, parse_c4, fmt_c4, ai_depth=8, ai_time=2),
}