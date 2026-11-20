# agentic/schemas.py
# Ce fichier définit CE QUE LE LLM REÇOIT en retour de chaque outil.
# Pydantic génère automatiquement le JSON Schema et valide les données.
from typing import Literal
from pydantic import BaseModel


class GameView(BaseModel):
    """Photo de la partie, renvoyée au LLM après chaque outil."""
    game_id: str                                  # le LLM doit le réutiliser à chaque appel
    game: Literal["tictactoe", "connect4"]        # "tictactoe" ou "connect4"
    board_text: str                               # plateau en texte (le LLM ne "voit" pas pygame)
    legal_moves: list[str]                        # ex: ["ligne 1, colonne 2", ...] lisible par le LLM
    is_over: bool
    winner: Literal["human", "ai", "draw"] | None = None
    whose_turn: Literal["human", "ai"] | None = None
    last_ai_move: str | None = None               # le coup que l'IA vient de jouer
    ai_stats: dict[str, float | int | None] | None = None  # explicabilité (nœuds, profondeur...)
    message: str                                  # résumé en français que le LLM peut reformuler