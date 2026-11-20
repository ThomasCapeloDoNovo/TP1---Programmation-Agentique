# agentic/mcp_server.py
# Expose le moteur comme "outils" MCP. Le LLM voit pour chaque outil :
#  - son nom, sa docstring (c'est sa seule façon de savoir QUAND l'utiliser)
#  - le JSON Schema de ses arguments (généré depuis les annotations + Field)
from typing import Annotated, Literal
from pydantic import Field
from mcp.server.fastmcp import FastMCP

from agentic import engine
from agentic.schemas import GameView

mcp = FastMCP("aussi")   # nom du serveur


@mcp.tool()
def new_game(
    game: Annotated[Literal["tictactoe", "connect4"], Field(description="Le jeu à jouer")],
    human_starts: Annotated[bool, Field(description="True si l'humain joue en premier")] = True,
    opponent: Annotated[Literal["minimax", "random"], Field(description="minimax = fort, random = coups aléatoires")] = "minimax",
) -> GameView:
    """Démarre une nouvelle partie contre l'IA et retourne le game_id à réutiliser dans les autres outils."""
    return engine.start_game(game, human_starts, opponent)


@mcp.tool()
def play_turn(
    game_id: Annotated[str, Field(description="Identifiant retourné par new_game")],
    col: Annotated[int | None, Field(description="Numéro de colonne, à partir de 1")] = None,
    row: Annotated[int | None, Field(description="Numéro de ligne, à partir de 1 (morpion seulement, inutile au puissance 4)")] = None,
) -> GameView:
    """Joue le coup de l'humain, puis l'IA répond automatiquement. Morpion : fournir row ET col (1 à 3). Puissance 4 : fournir seulement col (1 à 7)."""
    return engine.play_human_turn(game_id, row, col)


@mcp.tool()
def get_game(
    game_id: Annotated[str, Field(description="Identifiant retourné par new_game")],
) -> GameView:
    """Retourne l'état actuel de la partie (plateau, coups légaux, résultat)."""
    return engine.get_view(game_id)


@mcp.tool()
def suggest_move(
    game_id: Annotated[str, Field(description="Identifiant retourné par new_game")],
) -> str:
    """Conseille le meilleur coup à l'humain SANS le jouer."""
    return engine.suggest(game_id)


if __name__ == "__main__":
    # HTTP (et pas stdio) : le serveur reste vivant, donc SESSIONS garde les parties.
    mcp.run(transport="streamable-http")    # écoute sur http://127.0.0.1:8000/mcp