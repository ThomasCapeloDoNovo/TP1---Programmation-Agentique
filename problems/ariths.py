from enum import Enum
from .arith import ArithProblem
import random


#permet de générer une instance aléatoire pour le problème Arith
def generate():
    number = random.randint(1,20) #nombre à trouver
    size = random.randint(2,5) #nombre de nombres à utiliser pour retrouver number
    numbers = []
    for _ in range(size):
        numbers.append(random.randint(3,10)) #ajout d'un nombre random entre 1 et 20 dans la liste des nombres utilisables
    # print(number,numbers)
    return (
        number,
        tuple(numbers),
        ("+","-","/","*")
    )
        

class ArithInstance(Enum):
    FACILE = "facile"
    DIFFICILE = "difficile"
    # CONTOUR = "contour"
    # PIEGE = "Avec un piège"
    SANS_SOL = "sans_solution"
    ALEA = "aléatoire"

Ariths = {
    ArithInstance.FACILE: (
        24,
        (2,3,5,7),
        ("+","-","/","*")
    )
    ,
    ArithInstance.SANS_SOL:(
        1,
        (3,5),
        ("+","-","/","*")
    ),
    ArithInstance.DIFFICILE:(
        888,
        (13, 19, 23, 29, 37, 41),
        ("+","-","/","*")
    ),
    ArithInstance.ALEA: generate()
}

