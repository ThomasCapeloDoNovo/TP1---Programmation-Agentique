# Pour ajouter une instance de labyrinthe une dans problems/mazes.py suffit

# Pour ajouter un nouveau type de problème :
#   1. écrire sa classe dans problems/
#   2. l'ajouter ici : PROBLEM_LABELS, PROBLEMS et build()
#   3. écrire son affichage dans interface/gui/renderers.py (sans cela, l'état s'affiche en texte)

from .maze import MazeProblem
from .mazes import MAZES

# type = nom affiché dans le menu
PROBLEM_LABELS = {
    "maze": "Labyrinthe",
}

# type = noms des instances proposées dans le menu (pour le labyrinthe celles de mazes.py)
PROBLEMS = {
    "maze": list(MAZES.keys()),
}


def build(problem_type, instance):
    """Construit et retourne un nouveau Problem à partir de son type et du nom de l'instance."""
    if problem_type == "maze":
        return MazeProblem(MAZES[instance])

    raise ValueError(f"Type de problème inconnu : {problem_type}")
