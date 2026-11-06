import random
from .agent import Agent

class MCTSAgent(Agent):
    """ !! Agent à faire."""
    def __init__(self, time_limit=2.0, name="MCTS", ):
        super().__init__(name)

    def get_move(self, game, state):
        legal_actions = game.actions(state)
        if not legal_actions:
            return None
        return random.choice(legal_actions)
