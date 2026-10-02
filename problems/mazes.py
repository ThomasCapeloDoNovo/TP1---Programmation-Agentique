from enum import Enum
import random
"""Labyrinthes disponibles : 

Légende :
  #           mur
  S           départ
  G           but
  ' ' ou '.'  case normale (coût 1)
  '2' à '9'   le chiffre est le coût pour entrer dans la case
  
"""

class Difficulty(Enum):
    EASY = 1
    HARD = 2
    VHARD = 3
class MazeGenerator:

    @staticmethod
    def generate(width = 10, height = 10, difficulty = Difficulty.EASY):
        assert width >= 3
        assert height >= 3
        if width % 2 == 0:
            width -= 1
        if height % 2 == 0:
            height -= 1
        
        wall = []
        cell = {}

        cpt_groupe = 0
        for x in range(width):
            for y in range(height):
                if x % 2 == 0:
                    if y % 2 == 0:
                        cell[(x, y)] = cpt_groupe
                        cpt_groupe += 1
                    else:
                        wall.append((x, y))
                else:
                    wall.append((x, y))

        while len(set(cell.values())) > 1 and len(wall) > 0:
            wall_to_destroy = random.choice(wall)

            gr_base = -1
            other_gr = set()

            # regarde les 4 cellules autour
            coord_haut = (wall_to_destroy[0], wall_to_destroy[1] - 1)
            coord_gauche = (wall_to_destroy[0] - 1, wall_to_destroy[1])
            coord_bas = (wall_to_destroy[0], wall_to_destroy[1] + 1)
            coord_droite = (wall_to_destroy[0] + 1, wall_to_destroy[1])
            list_to_check = [coord_haut, coord_gauche, coord_bas, coord_droite]
            for c in list_to_check:
                if c not in wall and c in cell.keys():
                    if cell[c] not in other_gr:
                        if gr_base == -1:
                            gr_base = cell[c]
                        other_gr.add(cell[c])

            # fusion
            if len(other_gr) > 1:
                cell[wall_to_destroy] = gr_base
                for c, gr_id in cell.items():
                    if gr_id in other_gr:
                        cell[c] = gr_base
                wall.remove(wall_to_destroy)


        # généère la représentation texte
        maze = [
            "#" * (width + 2) 
        ]
        for y in range(height):
            row = "#"
            for x in range(width):
                if (x, y) in cell.keys():
                    if (x, y) == (0, 0):
                        row += "S"
                    elif(x, y) == (width - 1, height - 1):
                        row += "G"
                    else:
                        row += " "
                else:
                    row += "#"
            row += "#"
            maze.append(row)
        maze.append("#" * (width + 2))

        return maze
class MazeInstance(Enum):
    FACILE = "facile"
    CONTOUR = "contour"
    PIEGE = "Avec un piège"
    SANS_SOL = "sans_solution"
    ALEA = "aléatoire"

MAZES = {
    MazeInstance.FACILE: [
        "###############",
        "#S           G#",
        "# # ######### #",
        "# #           #",
        "# ########### #",
        "#             #",
        "###############",
    ],

    MazeInstance.CONTOUR: [
        "###############",
        "#S      #    G#",
        "####### # #####",
        "#       #     #",
        "# ########### #",
        "#             #",
        "###############",
    ],

    MazeInstance.PIEGE: [
        "###############",
        "#S  9        G#",
        "# # ######### #",
        "# #           #",
        "# ########### #",
        "#             #",
        "###############",
    ],

    MazeInstance.SANS_SOL: [
        "#######",
        "#S  # #",
        "#   #G#",
        "#   ###",
        "#######",
    ],

    MazeInstance.ALEA : MazeGenerator.generate(random.randint(10, 30), random.randint(10, 30))
}

