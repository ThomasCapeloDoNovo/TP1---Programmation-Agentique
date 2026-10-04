from enum import Enum
from .npuzzle import NPuzzleProblem

class NPuzzleInstance(Enum):
    FACILE = "facile"
    # CONTOUR = "contour"
    # PIEGE = "Avec un piège"
    # SANS_SOL = "sans_solution"
    # ALEA = "aléatoire"

NPuzzles = {
    NPuzzleInstance.FACILE: (
        (7,2,4),
        (5,NPuzzleProblem.EMPTY,6),
        (8,3,1)
    )
}