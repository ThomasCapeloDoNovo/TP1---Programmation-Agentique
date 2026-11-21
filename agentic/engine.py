# agentic/engine.py
#
# Moteur de jeu indépendant du MCP et du LLM.
#
# Responsabilités :
#
# - créer les parties
# - conserver les sessions
# - appliquer les coups
# - faire jouer l'IA
# - exposer l'état des parties sous forme de GameView
#
# Le moteur ne connaît jamais directement les détails
# d'un jeu comme TicTacToe ou Connect4.
#
# Toute logique spécifique est déléguée à l'adapter du jeu.

import uuid

from dataclasses import dataclass
from typing import Any

from games.agents.minimaxagent import MinimaxAgent
from games.agents.randomagent import RandomAgent

from . import GAMES
from .schemas import GameView

@dataclass(frozen=True)
class AgentConfig:
    """
    Paramètres utilisés pour créer un agent IA.

    Ces paramètres sont indépendants du jeu
    et décrivent uniquement la difficulté désirée.
    """

    # Profondeur maximale explorée par Minimax.
    max_depth: int = 9

    # Temps maximal accordé à la recherche d'un coup.
    time_limit: float = 2.0


@dataclass
class Session:
    """
    Partie actuellement active.

    Une session contient tout ce qui est nécessaire
    pour retrouver une partie à partir de son game_id.
    """

    # Nom du jeu.
    game_name: str

    # Instance du jeu.
    game: Any

    # Etat actuel de la partie.
    #
    # Les états sont immuables :
    # jouer un coup produit un nouvel état.
    state: Any

    # Identifiant du joueur humain (game.player1 ou player2)
    human: int

    # Agent contrôlant l'adversaire.
    agent: Any

    # Configuration utilisée pour créer l'agent.
    agent_config: AgentConfig

    def to_view(
        self,
        game_id: str,
        ai_move=None,
        message: str | None = None,
    ) -> GameView:
        """
        Construit une vue sérialisable de la partie.

        Cette méthode transforme l'état interne du moteur en GameView destiné au LLM.
        """
        definition = GAMES[self.game_name]
        adapter = definition.adapter()
        game = self.game
        is_over = game.is_terminal(self.state)
        winner = None

        if is_over:
            native_winner = game.winner(self.state)
            if native_winner is None:
                winner = "draw"
            elif native_winner == self.human:
                winner = "human"
            else:
                winner = "ai"
            legal_moves = []

        if not is_over:
            legal_moves = [
                adapter.format_move(move)
                for move in game.actions(self.state)
            ]

        stats = {
            "nodes_explored": getattr(self.agent, "nodes_explored", None),
            "depth_reached": getattr(self.agent, "last_completed_depth",None),
        }

        ai_stats = stats if any(v is not None for v in stats.values()) else None

        exposed_state = adapter.build_state(self.state)

        ## !!
        renderer = definition.renderer()

        text_render = renderer.render(
            state=exposed_state,
            format="text",
        )
        ## 

        return GameView(
            game_id=game_id,
            game=self.game_name,
            state=exposed_state,

            # !!
            state_text_render=text_render,
            #

            legal_moves=legal_moves,
            is_over=is_over,
            winner=winner,
            whose_turn=(None if is_over else "human"),
            last_ai_move=(
                None
                if ai_move is None
                else adapter.format_move(ai_move)
            ),
            ai_stats=ai_stats,
            message=message,
        )

# Mémoire du serveur : game_id -> Session.
# Le LLM ne manipule QUE le game_id, jamais le plateau (évite les erreurs de recopie).
SESSIONS: dict[str, Session] = {}

class GameEngine:
    """
    API principale du moteur.
    """

    @staticmethod
    def _create_agent(
        kind: str,
        config: AgentConfig,
    ):
        """
        Construit l'agent demandé.
        """
        if kind == "minimax":
            return MinimaxAgent(max_depth=config.max_depth, time_limit=config.time_limit)
        if kind == "random":
            return RandomAgent()
        raise ValueError(f"Adversaire inconnu : {kind}. Les agents disponibles sont : minimax et random")

    @staticmethod
    def _get_session(
        game_id: str,
    ) -> Session:
        """
        Récupère une session active.
        """
        session = SESSIONS.get(game_id)
        if session is None:
            raise ValueError(f"game_id inconnu : '{game_id}'. Crée d'abord une partie avec new_game.")
        return session

    @staticmethod
    def _play_ai(
        session: Session,
    ) -> Any:
        """
        Fait jouer l'IA et retourne le coup choisi.
        """
        move = session.agent.get_move(session.game,session.state)
        session.state = session.game.result(session.state, move)

        return move

    @classmethod
    def start_game(
        cls,
        game_name: str,
        human_starts: bool,
        opponent: str,
        ai_depth: int = 9,
        ai_time: float = 1.0,
    ) -> GameView:
        """
        Crée une nouvelle partie.
        """
        definition = GAMES[game_name]

        adapter = definition.adapter()

        game = adapter.create_game()

        config = AgentConfig(max_depth=ai_depth,time_limit=ai_time)

        human = (game.player1 if human_starts else game.player2 )

        session = Session(
            game_name=game_name,
            game=game,
            state=game.initial_state(),
            human=human,
            agent=cls._create_agent(
                opponent,
                config,
            ),
            agent_config=config,
        )

        game_id = uuid.uuid4().hex[:8]

        SESSIONS[game_id] = session

        ai_move = None

        if not human_starts:
            ai_move = cls._play_ai(session)

        return session.to_view(
            game_id=game_id,
            ai_move=ai_move,
            message="Nouvelle partie créée.",
        )


    @classmethod
    def play_turn(
        cls,
        game_id: str,
        row: int | None,
        col: int | None,
    ) -> GameView:
        """
        Joue le tour de l'humain.
        """

        session = cls._get_session(game_id)

        definition = GAMES[session.game_name]

        adapter = definition.adapter()

        if session.game.is_terminal(session.state):
            raise ValueError("La partie est terminée.")

        move = adapter.parse_move(row=row,col=col)

        if not session.game.is_legal(session.state,move):

            legal = [adapter.format_move(m)for m in session.game.actions(session.state)]

            raise ValueError(f"Coup illégal. " f"Coups légaux : {legal}")

        session.state = (session.game.result(session.state, move))

        ai_move = None
        if not session.game.is_terminal(session.state):
            ai_move = cls._play_ai(session)

        return session.to_view(
            game_id=game_id,
            ai_move=ai_move,
            message="Coup de l'humain joué.",
        )

    @classmethod
    def get_game(
        cls,
        game_id: str,
    ) -> GameView:
        """
        Retourne l'état actuel de la partie.
        """

        session = cls._get_session(game_id)
        print(session.to_view(game_id))
        return session.to_view(game_id)

    @classmethod
    def suggest_move(
        cls,
        game_id: str,
    ) -> str:
        """
        Calcule un coup conseillé sans le jouer.

        La partie n'est jamais modifiée : un Minimax temporaire
        est créé uniquement pour analyser la position actuelle.
        """

        session = cls._get_session(game_id)

        if session.game.is_terminal(session.state):
            raise ValueError("La partie est terminée.")

        helper = MinimaxAgent(
            max_depth=session.agent_config.max_depth,
            time_limit=session.agent_config.time_limit,
        )

        move = helper.get_move(session.game,session.state)

        adapter = GAMES[session.game_name].adapter()

        return (
            f"Coup conseillé : {adapter.format_move(move)} "
            f"(Minimax, profondeur atteinte {helper.last_completed_depth})"
        )

    @classmethod
    def render_game(
        cls,
        game_id: str,
        format: str = "text",
    ):
        """
        Génère une représentation du plateau.

        Le format dépend du renderer associé au jeu.
        """

        session = cls._get_session(game_id)

        game_def = GAMES[session.game_name]

        renderer = game_def.renderer()

        state = game_def.adapter().build_state(
            session.state
        )

        return renderer.render(
            state=state,
            format=format,
        )