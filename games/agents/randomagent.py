import random
from .agent import Agent

class RandomAgent(Agent):
    """Agent choisissant uniformément et aléatoirement parmi les actions légales."""
    def __init__(self, name="Aléatoire"):
        super().__init__(name)

    def get_move(self, game, state):
        legal_actions = game.actions(state)
        if not legal_actions:
            return None
        return random.choice(legal_actions)
