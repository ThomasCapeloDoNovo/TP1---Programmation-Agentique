# agentic/schemas.py
# Ce fichier définit CE QUE LE LLM REÇOIT en retour de chaque outil.
# Pydantic génère automatiquement le JSON Schema et valide les données.
from typing import Literal
from pydantic import BaseModel

class Connect4State(BaseModel):
    grid: list[list[int]]

class TicTacToeState(BaseModel):
    grid: list[list[int]]

class GomokuState(BaseModel):
    grid: list[list[int]]

type LI_STATE_LLM = Connect4State | TicTacToeState | GomokuState

class GameView(BaseModel):
    """
    Représentation canonique d'une partie.

    Cet objet est la seule "vérité" exposée au LLM.
    Le LLM ne conserve normalement que le game_id et peut récupérer l'état réel de la partie à n'importe quel moment avec l'outil get_game().

    Cela limite fortement les hallucinations puisque l'état n'est jamais reconstruit à partir de l'historique du chat.
    """

    # Identifiant unique de la partie. Permet de retrouver la session stockée côté serveur.
    game_id: str

    # Nom du jeu associé à cette partie. Sert notamment à savoir quelles règles appliquer et quels outils de rendu utiliser.
    game: Literal["tictactoe", "connect4", "gomoku"]

    # État brut du jeu.
    # Cet état doit contenir suffisamment d'informations pour reconstruire entièrement la partie sans ambiguïté.
    state: LI_STATE_LLM

    # Représentation officielle du plateau destinée aux interfaces textuelles et au LLM. !! temporaire ... 
    state_text_render: str

    # Liste des coups actuellement légaux.
    # Cette liste est formatée pour être facilement comprise par le LLM afin qu'il puisse jouer sans avoir à deviner les règles du jeu.
    # Exemple :
    # [
    #     "ligne 1, colonne 2",
    #     "ligne 3, colonne 1"
    # ]
    legal_moves: list[str]

    # True si la partie est terminée.
    is_over: bool

    # Gagnant de la partie lorsque is_over vaut True.
    # human : le joueur humain gagne
    # ai    : l'intelligence artificielle gagne
    # draw  : match nul
    # None  : partie encore en cours
    winner: Literal["human", "ai", "draw"] | None = None

    # Joueur devant jouer le prochain coup.
    # None lorsque la partie est terminée.
    whose_turn: Literal["human", "ai"] | None = None

    # Dernier coup joué par l'IA.
    # Champ utile pour que le LLM puisse expliquer
    # naturellement l'évolution de la partie à l'utilisateur.
    last_ai_move: str | None = None

    # Informations d'explicabilité provenant de l'agent.
    # Exemple :
    # {
    #     "nodes_explored": 2500,
    #     "depth_reached": 8
    # }
    # Peut être None pour des agents simples comme un agent aléatoire.
    ai_stats: dict[str, float | int | None] | None = None

    # Message optionnel décrivant ce qui vient de se passer.
    # Ce champ est principalement destiné à améliorer l'expérience conversationnelle.
    message: str | None = None