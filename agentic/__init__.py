# agentic/__init__.py
"""
Registre central des jeux disponibles.

Le moteur agentique ne connaît jamais directement
TicTacToe, Connect4 ou les futurs jeux.

Il passe toujours par ce registre.

Pour ajouter un nouveau jeu :

1. Définir son modèle d'état (Pydantic)
2. Créer son adapter
3. L'enregistrer ici

Aucun changement ne devrait normalement être nécessaire
dans le moteur.
"""

from dataclasses import dataclass
from typing import Type

from .adapters.tictactoeadapter import TicTacToeAdapter, TicTacToeState
from .adapters.connect4adapter import Connect4Adapter, Connect4State
from .adapters.gomokuadapter import GomokuAdapter, GomokuState

from .renderers.tictactoerenderer import TicTacToeRenderer
from .renderers.connect4renderer import Connect4Renderer
from .renderers.gomokurenderer import GomokuRenderer


@dataclass(frozen=True)
class GameDefinition:
    """
    Décrit tout ce dont le moteur a besoin pour intégrer un jeu.

    state_model :
        Modèle Pydantic représentant l'état du jeu exposé au LLM.

    adapter :
        Adaptateur faisant le lien entre le moteur générique et l'implémentation concrète du jeu.
    """

    state_model: Type
    adapter: Type
    renderer: Type


GAMES = {
    "tictactoe": GameDefinition(
        state_model=TicTacToeState,
        adapter=TicTacToeAdapter,
        renderer=TicTacToeRenderer,
    ),
    "connect4": GameDefinition(
        state_model=Connect4State,
        adapter=Connect4Adapter,
        renderer=Connect4Renderer,
    ),
    "gomoku": GameDefinition(
        state_model=GomokuState,
        adapter=GomokuAdapter,
        renderer=GomokuRenderer,
    ),
}