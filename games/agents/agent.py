import time
import random

class Agent:
    """Classe de base abstraite pour tous les agents."""
    def __init__(self, name="Agent"):
        self.name = name

    def get_move(self, game, state):
        """Retourne l'action choisie par l'agent pour l'état donné."""
        raise NotImplementedError

