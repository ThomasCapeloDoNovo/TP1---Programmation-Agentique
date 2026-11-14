from abc import ABC, abstractmethod


class Game(ABC):
    """Contrat commun des jeux à deux joueurs.

    ``is_terminal(state)`` renvoie un booléen.
    ``winner(state)`` renvoie l'identifiant du gagnant, ou None (nul / aucun gagnant).
    ``utility(state, player)`` est exacte aux états terminaux : +1 victoire,
    0 nul, -1 défaite, du point de vue de ``player``.
    Les états doivent être immuables/hashables et result() ne modifie pas l'état reçu.
    """

    def __init__(self, player1=1, player2=2):
        self.player1 = player1
        self.player2 = player2

    @abstractmethod
    def initial_state(self):
        """Retourne l'état initial."""

    @abstractmethod
    def player_to_move(self, state):
        """Retourne le joueur dont c'est le tour."""

    @abstractmethod
    def actions(self, state):
        """Retourne les actions légales depuis cet état."""

    @abstractmethod
    def result(self, state, action):
        """Retourne le nouvel état après l'action, sans muter state."""

    @abstractmethod
    def is_terminal(self, state):
        """Retourne True si la partie est terminée, sinon False."""

    def winner(self, state):
        """Retourne le gagnant, ou None en l'absence de gagnant."""
        return None

    def utility(self, state, player):
        """Utilité exacte d'un état terminal du point de vue de player."""
        if not self.is_terminal(state):
            raise ValueError("utility() ne s'applique qu'aux états terminaux")
        winner = self.winner(state)
        if winner is None:
            return 0
        return 1 if winner == player else -1

    def is_legal(self, state, action):
        """Vérifie la légalité d'une action. Les jeux concrets devraient surcharger."""
        return action in self.actions(state)

    def evaluate(self, state, player):
        """Heuristique pour les états non terminaux (neutre par défaut)."""
        return 0

    def display(self, state):
        print(state)
