import math
import random
import time

from .agent import Agent


class Node_MCTS:
    def __init__(self, game, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.untried_actions = (
            [] if game.is_terminal(state) else list(game.actions(state))
        )
        self.visits = 0
        self.value = 0.0


class MCTSAgent(Agent):
    """Agent Monte-Carlo Tree Search utilisant UCT et des simulations aléatoires."""

    def __init__(self, time_limit=2.0, exploration_constant=1, max_simulations=None, name="MCTS"):
        super().__init__(name)
        if time_limit <= 0:
            raise ValueError("la limite de temps doit être strictement positive")
        if exploration_constant < 0:
            raise ValueError("exploration_constant doit être positif ou nul")
        if max_simulations is not None and max_simulations < 1:
            raise ValueError("max_simulations doit être >= 1")

        self.time_limit = time_limit
        self.max_simulations = max_simulations
        self.exploration_constant = exploration_constant
        self.iterations = 0
        self.last_simulations_run = 0
        self.root_visits = {}
        self.search_time = 0.0

    def get_move(self, game, state):
        if game.is_terminal(state):
            return None

        legal_actions = game.actions(state)
        if not legal_actions:
            return None

        start_time = time.monotonic() 
        deadline = start_time + self.time_limit
        root_player = game.player_to_move(state)
        root = Node_MCTS(game, state)
        self.iterations = 0
        self.last_simulations_run = 0
        self.root_visits = {}

        while (self.iterations < self.max_simulations
               if self.max_simulations is not None
               else time.monotonic() < deadline):
            ### Sélection
            node = root

            while not game.is_terminal(node.state) and not node.untried_actions:
                #choix du noeud enfant le plus prometteur 
                node = self._select_child(game, node, root_player)

            ### Expansion 
            if not game.is_terminal(node.state):
                action = node.untried_actions.pop(random.randrange(len(node.untried_actions)))
                child_state = game.result(node.state, action)
                child = Node_MCTS(game, child_state, parent=node, action=action)
                node.children.append(child)
                node = child

            ### Simulation 
            reward = self.simulate(game, node.state, root_player)

            ### Backpropagation
            while node is not None:
                node.visits += 1
                node.value += reward
                node = node.parent

            self.iterations += 1

        self.search_time = time.monotonic() - start_time
        self.last_simulations_run = self.iterations
        self.root_visits = {child.action: child.visits for child in root.children}
        if not root.children:
            return legal_actions[0]

        best_child = max(
            root.children,
            key=lambda child: (child.visits, child.value / child.visits),
        )
        return best_child.action

    def _select_child(self, game, node, root_player):
        maximizing = game.player_to_move(node.state) == root_player
        log_parent_visits = math.log(node.visits)

        def uct(child):
            mean_value = child.value / child.visits
            exploitation = mean_value if maximizing else -mean_value
            exploration = self.exploration_constant * math.sqrt(
                log_parent_visits / child.visits
            )
            return exploitation + exploration

        return max(node.children, key=uct)

    def simulate(self, game, state, root_player):
        while True:
            if game.is_terminal(state):
                return float(game.utility(state, root_player))

            actions = game.actions(state)
            if not actions:
                raise ValueError("État non terminal sans action légale")
            state = game.result(state, random.choice(actions))
