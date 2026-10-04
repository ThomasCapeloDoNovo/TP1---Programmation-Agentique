from enum import Enum
from .arith import ArithProblem

class ArithInstance(Enum):
    FACILE = "facile"
    # CONTOUR = "contour"
    # PIEGE = "Avec un piège"
    # SANS_SOL = "sans_solution"
    # ALEA = "aléatoire"

Ariths = {
    ArithInstance.FACILE: (
        24,
        (2,3,5,7),
        ("+","-","/","*")
    )
}