# agentic/engine.py
# Gère les parties en cours. Aucune dépendance au LLM ni à MCP : on peut
# donc le tester seul
import uuid
from dataclasses import dataclass
from typing import Any

from games.agents.minimaxagent import MinimaxAgent
from games.agents.randomagent import RandomAgent
from .schemas import GameView
from .specs import SPECS, GameSpec, render_grid


@dataclass
class Session:
    spec: GameSpec
    game: Any
    state: Any       # état courant (immuable) : on le REMPLACE à chaque coup
    human: int       # identifiant du joueur humain (game.player1 ou player2)
    agent: Any       # l'IA adverse


# Mémoire du serveur : game_id -> Session.
# Le LLM ne manipule QUE le game_id, jamais le plateau (évite les erreurs de recopie).
SESSIONS: dict[str, Session] = {}


def _make_agent(kind: str, spec: GameSpec):
    if kind == "minimax":
        return MinimaxAgent(max_depth=spec.ai_depth, time_limit=spec.ai_time)
    if kind == "random":
        return RandomAgent()
    raise ValueError(f"Adversaire inconnu : {kind}. Les agents disponibles sont : minimax et random")


def _get(game_id: str) -> Session:
    s = SESSIONS.get(game_id)
    if s is None:
        raise ValueError(f"game_id inconnu : '{game_id}'. Crée d'abord une partie avec new_game.")
    return s


def _ai_play(s: Session) -> Any:
    """L'IA choisit et joue un coup. Retourne l'action native jouée."""
    move = s.agent.get_move(s.game, s.state)   # ton MinimaxAgent fait le travail
    s.state = s.game.result(s.state, move)     # result() renvoie un NOUVEL état
    return move


def _view(game_id: str, s: Session, ai_move=None, note: str = "") -> GameView:
    g, st, spec = s.game, s.state, s.spec
    over = g.is_terminal(st)
    w = g.winner(st) if over else None
    winner = None
    if over:
        winner = "draw" if w is None else ("human" if w == s.human else "ai")

    human_sym = "X" if s.human == g.player1 else "O"
    ai_sym = "O" if human_sym == "X" else "X"
    board = render_grid(g, st) + f"\n(humain = {human_sym}, IA = {ai_sym})"

    # Statistiques d'explicabilité de l'agent Minimax (None pour RandomAgent)
    stats = {
        "nodes_explored": getattr(s.agent, "nodes_explored", None),
        "depth_reached": getattr(s.agent, "last_completed_depth", None),
    }
    ai_stats = stats if any(v is not None for v in stats.values()) else None

    legal = [] if over else [spec.format_move(a) for a in g.actions(st)]
    msg = note
    if ai_move is not None:
        msg += f" L'IA a joué : {spec.format_move(ai_move)}."
    if over:
        msg += {"human": " Partie terminée : l'humain gagne.",
                "ai": " Partie terminée : l'IA gagne.",
                "draw": " Partie terminée : match nul."}[winner]
    else:
        msg += " C'est au tour de l'humain."

    return GameView(
        game_id=game_id, game=spec.name, board_text=board, legal_moves=legal,
        is_over=over, winner=winner,
        whose_turn=None if over else "human",
        last_ai_move=None if ai_move is None else spec.format_move(ai_move),
        ai_stats=ai_stats, message=msg.strip(),
    )


# API du moteur (appelée par les outils MCP)
def start_game(game_name: str, human_starts: bool, opponent: str) -> GameView:
    spec = SPECS[game_name]
    g = spec.make_game()
    human = g.player1 if human_starts else g.player2   # player1 commence toujours
    s = Session(spec, g, g.initial_state(), human, _make_agent(opponent, spec))
    gid = uuid.uuid4().hex[:8]
    SESSIONS[gid] = s
    ai_move = None if human_starts else _ai_play(s)    # si l'IA commence, elle joue tout de suite
    return _view(gid, s, ai_move, note="Nouvelle partie créée.")


def play_human_turn(game_id: str, row: int | None, col: int | None) -> GameView:
    s = _get(game_id)
    if s.game.is_terminal(s.state):
        raise ValueError("La partie est terminée. Crée-en une nouvelle avec new_game.")
    move = s.spec.parse_move(row, col)                 # arguments -> action native
    if not s.game.is_legal(s.state, move):
        legal = [s.spec.format_move(a) for a in s.game.actions(s.state)]
        # Ce message est renvoyé au LLM : il peut donc se corriger tout seul.
        raise ValueError(f"Coup illégal. Coups légaux : {legal}")
    s.state = s.game.result(s.state, move)             # coup humain
    ai_move = None
    if not s.game.is_terminal(s.state):
        ai_move = _ai_play(s)                          # réponse immédiate de l'IA
    return _view(game_id, s, ai_move, note="Coup de l'humain joué.")


def get_view(game_id: str) -> GameView:
    return _view(game_id, _get(game_id), note="")


def suggest(game_id: str) -> str:
    s = _get(game_id)
    if s.game.is_terminal(s.state):
        raise ValueError("La partie est terminée, aucun conseil possible.")
    # On crée un Minimax jetable : get_move() joue pour le joueur dont c'est le tour
    helper = MinimaxAgent(max_depth=s.spec.ai_depth, time_limit=s.spec.ai_time)
    move = helper.get_move(s.game, s.state)
    return (f"Coup conseillé : {s.spec.format_move(move)} "
            f"(Minimax, profondeur atteinte {helper.last_completed_depth}).")