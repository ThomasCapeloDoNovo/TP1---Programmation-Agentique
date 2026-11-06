import time
from .agent import Agent

class MinimaxAgent(Agent):
    """Agent Minimax avec Approfondissement Itératif (IDS) et élagage Alpha-Bêta."""
    def __init__(self, max_depth=5, time_limit=2.0, eval_fn=None, name="Minimax"):
        super().__init__(name)
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.eval_fn = eval_fn
        
        # Statistiques d'explicabilité
        self.last_completed_depth = 0
        self.nodes_explored = 0
        self.search_time = 0.0

    def get_move(self, game, state):
        player = game.player_to_move(state)
        legal_actions = game.actions(state)
        if not legal_actions:
            return None

        eval_function = self.eval_fn or (lambda s, p: game.evaluate(s, p))
        
        best_move = legal_actions[0]  # Coup de secours par défaut si le temps est trop court
        start_time = time.time()
        self.nodes_explored = 0
        self.last_completed_depth = 0

        # Approfondissement itératif de 1 à max_depth
        for depth in range(1, self.max_depth + 1):
            try:
                current_best_move = None
                best_value = float('-inf')
                alpha = float('-inf')
                beta = float('inf')

                for action in legal_actions:
                    if time.time() - start_time > self.time_limit:
                        raise TimeoutError()
                    
                    next_state = game.result(state, action)
                    value = self._min_value(game, next_state, depth - 1, alpha, beta, player, start_time, eval_function)
                    
                    if value > best_value:
                        best_value = value
                        current_best_move = action
                    alpha = max(alpha, best_value)

                # Si l'itération est allée au bout dans le temps imparti, on valide le résultat
                best_move = current_best_move
                self.last_completed_depth = depth

            except TimeoutError:
                break

        self.search_time = time.time() - start_time

        return best_move

    def _max_value(self, game, state, depth, alpha, beta, player, start_time, eval_fn):
        if time.time() - start_time > self.time_limit:
            raise TimeoutError()
        
        self.nodes_explored += 1
        is_term, utility = game.is_terminal(state)

        # !! fct eval --
        if is_term:
            if utility == player: return 1
            elif utility is None: return 0
            else: return -1
        if depth == 0:
            return eval_fn(state, player)
        # -- 

        v = float('-inf')
        for action in game.actions(state):
            next_state = game.result(state, action)
            v = max(v, self._min_value(game, next_state, depth - 1, alpha, beta, player, start_time, eval_fn))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def _min_value(self, game, state, depth, alpha, beta, player, start_time, eval_fn):
        if time.time() - start_time > self.time_limit:
            raise TimeoutError()
        
        self.nodes_explored += 1
        is_term, utility = game.is_terminal(state)

        # -- fct eval
        if is_term:
            if utility == player: return 1
            elif utility is None: return 0
            else: return -1
        if depth == 0:
            return eval_fn(state, player)
        # -- 

        v = float('inf')
        for action in game.actions(state):
            next_state = game.result(state, action)
            v = min(v, self._max_value(game, next_state, depth - 1, alpha, beta, player, start_time, eval_fn))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v