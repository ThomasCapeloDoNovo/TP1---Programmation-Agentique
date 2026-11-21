# agentic/adapters.py
#
# Un adapter sert d'intermédiaire entre le moteur générique et un jeu
# particulier (TicTacToe, Connect4, etc.).
#
# Le moteur ne doit pas connaître les détails des jeux. Il délègue :
#
# - la création du jeu
# - la conversion des coups
# - la représentation des états
# - l'affichage des coups
#
# à l'adapter approprié.

from abc import ABC, abstractmethod

class GameAdapter(ABC):
    """
    Contrat commun à tous les jeux.

    Pour ajouter un nouveau jeu, il suffit normalement de créer une nouvelle classe héritant de GameAdapter et de l'enregistrer dans le registre des jeux.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom unique du jeu."""
        pass

    @abstractmethod
    def create_game(self):
        """
        Construit une nouvelle instance du jeu.
        """
        pass

    # peut-être à modifier via args/kwargs
    @abstractmethod
    def parse_move(
        self,
        row: int | None,
        col: int | None,
    ):
        """
        Convertit les paramètres reçus depuis le MCP
        en action native comprise par le jeu.
        """
        pass

    @abstractmethod
    def format_move(self, move) -> str:
        """
        Convertit une action native en texte lisible
        pour un humain ou un LLM.
        """
        pass

    @abstractmethod
    def build_state(self, state):
        """
        Transforme l'état interne du jeu en objet Pydantic.

        Cela permet de renvoyer une représentation validée
        et indépendante de l'implémentation interne du jeu.
        """
        pass
