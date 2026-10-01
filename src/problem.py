from abc import ABC, abstractmethod


class Problem(ABC):
    """Interface (normalement) commune à tous les problèmes

    Pour ajouter un problème :
      1. créer une sous-classe (dans problems/) qui définit les 4 méthodes abstraites qui sont dans la suite du fichier
      2. la mettre dans problems/__init__.py

    Contraintes sur l'état :
      - hashable (tuple, pas liste) : le graph-search s'en sert comme clé de dictionnaire
      - result() ne doit pas modifier l'état reçu, mais en renvoyer un nouveau
    """

    def __init__(self, initial_state):
        self.initial_state = initial_state

    @abstractmethod
    def actions(self, state):
        """A(s) : liste des actions légales depuis cet état."""

    @abstractmethod
    def result(self, state, action):
        """RESULT(s, a) : nouvel état obtenu en appliquant l'action."""

    @abstractmethod
    def goal_test(self, state):
        """True si l'état est un but."""

    def step_cost(self, state, action, next_state):
        """c(s, a, s') : coût d'une action (1 par défaut). À redéfinir si les coûts varient."""
        return 1

    @abstractmethod
    def heuristic(self, state):
        """h(s) : estimation du coût restant jusqu'au but.
        Elle doit être admissible pour qu'A* reste optimal."""

    def display(self, state):
        """Affichage console d'un état """
        print(state)
