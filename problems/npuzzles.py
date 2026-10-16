from enum import Enum
from .npuzzle import NPuzzleProblem

class NPuzzleInstance(Enum):
    FACILE = "facile"
    MOYENNE = "moyenne"
    DIFFICILE = "difficile"
    # CONTOUR = "contour"
    # PIEGE = "Avec un piège"
    # SANS_SOL = "sans_solution"
    # ALEA = "aléatoire"

NPuzzles = {
    NPuzzleInstance.FACILE: (
        (7,2,4),
        (5,NPuzzleProblem.EMPTY,6),
        (8,3,1)
    ),
    NPuzzleInstance.MOYENNE: (
    (12, 1, 10, 2),
    (7, 11, 4, 14),
    (5, NPuzzleProblem.EMPTY, 9, 3),
    (13, 6, 15, 8)
),
    NPuzzleInstance.DIFFICILE : (
    (1, 2, 3, 4, 5),
    (6, 7, 8, 10, 9),
    (11, 12, 13, 14, 15),
    (16, 17, 19, 18, 20),
    (21, 22, NPuzzleProblem.EMPTY, 23, 24)
    )
}