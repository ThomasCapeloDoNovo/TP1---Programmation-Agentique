from abc import ABC, abstractmethod


class Game(ABC):
    """Interface commune à tous les jeux

    Contraintes sur l'état :
      - hashable (tuple, pas liste)
      - result() ne doit pas modifier l'état reçu, mais en renvoyer un nouveau
    """

    def __init__(self, player1 = 1, player2 = 2):
        self.player1 = player1
        self.player2 = player2

    @abstractmethod
    def initial_state(self):
        """état du jeu initial"""

    @abstractmethod
    def player_to_move(self, state):
        """retourne le joueur associé au tour"""

    @abstractmethod
    def actions(self, state):
        """A(s) : liste des actions légales depuis cet état."""

    @abstractmethod
    def result(self, state, action):
        """RESULT(s, a) : nouvel état obtenu en appliquant l'action."""

    @abstractmethod
    def is_terminal(self, state):
        """True si le jeu est fini."""

    def is_legal(self, state, action):
        """True si l'action est légale"""
        return True

    def evaluate(self, state, player):
        """retourne l'evaluation de l'état pour le jouer player"""
        return 0

    def display(self, state):
        """Affichage console d'un état """
        print(state)
