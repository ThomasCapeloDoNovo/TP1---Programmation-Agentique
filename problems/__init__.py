# Pour ajouter une instance de labyrinthe une dans problems/mazes.py suffit

# Pour ajouter un nouveau type de problème :
#   1. écrire sa classe dans problems/
#   2. l'ajouter ici : PROBLEM_LABELS, PROBLEMS et build()
#   3. écrire son affichage dans interface/gui/renderers.py (sans cela, l'état s'affiche en texte)

from .maze import MazeProblem
from .mazes import MAZES, MazeInstance
from .mazes import MazeGenerator

from .npuzzle import NPuzzleProblem
from .npuzzles import NPuzzles, NPuzzleInstance

from .arith import ArithProblem
from .ariths import Ariths, ArithInstance

# type = nom affiché dans le menu
PROBLEM_LABELS = {
    "maze": "Labyrinthe",
    "npuzzle": "N-Puzzle",
    "arith": "Jeu arithmétique"
}

# type = noms des instances proposées dans le menu (pour le labyrinthe celles de mazes.py)
PROBLEMS = {
    "maze": list(MAZES.keys()),
    "npuzzle": list(NPuzzles.keys()),
    "arith": list(Ariths.keys())
}


def build(problem_type, instance, **kwargs):
    """Construit et retourne un nouveau Problem à partir de son type et du nom de l'instance."""
    if problem_type == "maze":
        # if instance == MazeInstance.ALEA:
        #     print(MazeGenerator.generate(
        #                         kwargs["width"],
        #                         kwargs["heigth"]
        #                     ))
        #     return MazeProblem(
        #         MazeGenerator.generate(
        #             kwargs["width"],
        #             kwargs["heigth"]
        #         )
        #     )
        return MazeProblem(MAZES[instance])

    if problem_type == "npuzzle":
        return NPuzzleProblem(NPuzzles[instance])

    if problem_type == "arith":
        return ArithProblem(Ariths[instance])

    raise ValueError(f"Type de problème inconnu : {problem_type}")
