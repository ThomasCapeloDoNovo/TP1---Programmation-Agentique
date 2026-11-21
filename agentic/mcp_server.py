# agentic/mcp_server.py
#
# Expose le moteur comme outils MCP.
#
# Le LLM voit pour chaque outil :
#
# - son nom
# - sa docstring
# - le schéma JSON de ses arguments
#
# Le moteur reste indépendant du MCP.
# Ce fichier fait uniquement le lien entre MCP et GameEngine.

from typing import Annotated, Literal

from pydantic import Field
from mcp.server.fastmcp import FastMCP

from agentic.engine import GameEngine
from agentic.schemas import GameView


# Nom du serveur MCP.
mcp = FastMCP("aussi")


@mcp.tool()
def new_game(
    game: Annotated[Literal["tictactoe", "connect4"], Field(description="Le jeu à jouer")],
    human_starts: Annotated[bool, Field(description="True si l'humain joue en premier")] = True,
    opponent: Annotated[Literal["minimax", "random"], Field(description="minimax = fort, random = coups aléatoires")] = "minimax",
    ai_depth: Annotated[int,Field(description=("Profondeur maximale de recherche de Minimax"),ge=1,)] = 9,
    ai_time: Annotated[float,Field(description=("Temps maximal accordé à Minimax pour choisir un coup (secondes)"),gt=0,)] = 2.0,
) -> GameView:
    """Démarre une nouvelle partie contre l'IA et retourne le game_id à réutiliser dans les autres outils."""

    return GameEngine.start_game(
        game_name=game,
        human_starts=human_starts,
        opponent=opponent,
        ai_depth=ai_depth,
        ai_time=ai_time,
    )


@mcp.tool()
def play_turn(
    game_id: Annotated[str, Field(description="Identifiant retourné par new_game")],
    col: Annotated[int | None, Field(description="Numéro de colonne, à partir de 1")] = None,
    row: Annotated[int | None, Field(description="Numéro de ligne, à partir de 1 (morpion seulement, inutile au puissance 4)")] = None,
) -> GameView:
    """Joue le coup de l'humain, puis l'IA répond automatiquement."""
    return GameEngine.play_turn(
        game_id=game_id,
        row=row,
        col=col,
    )


@mcp.tool()
def get_game(
    game_id: Annotated[str, Field(description="Identifiant retourné par new_game")],
) -> GameView:
    """Retourne l'état actuel de la partie (plateau, coups légaux, résultat)."""
    return GameEngine.get_game(
        game_id
    )


@mcp.tool()
def suggest_move(
    game_id: Annotated[str, Field(description="Identifiant retourné par new_game")],
) -> str:
    """Conseille le meilleur coup à l'humain SANS le jouer."""
    return GameEngine.suggest_move(
        game_id
    )

# !! malheureusement hallucine et ne l'appelle jamais 
# @mcp.tool()
# def render_game(
#     game_id: Annotated[str,Field(description="Identifiant retourné par new_game")],
#     format: Annotated[Literal["text", "image"],Field(description="Format du rendu")] = "text",
# ):
#     """Retourne la représentation officielle du plateau à afficher mot pour mot à l'utilisateur."""
#     return GameEngine.render_game(
#         game_id=game_id,
#         format=format,
#     )

# HTTP (et pas stdio) : le serveur reste vivant, donc SESSIONS garde les parties.
mcp.run(transport="streamable-http")    # écoute sur http://127.0.0.1:8000/mcp