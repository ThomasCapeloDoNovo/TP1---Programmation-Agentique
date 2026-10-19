
from src.problem import Problem

class NPuzzleProblem(Problem):
    """N-Puzzle.

    puzzle  : tuple de tuple
    état  : tuple de tuple
    coût  : 1 par case

    Pour changer les règles : actions() pour les déplacements autorisés (ex. step_cost() pour les coûts, heuristic() pour l'estimation.
    """

    MOVES = {
        "HAUT": (-1, 0),
        "BAS": (1, 0),
        "GAUCHE": (0, -1),
        "DROITE": (0, 1),
    }

    EMPTY = "-"

    def __init__(self, puzzle):
        self.puzzle = puzzle

        self.initial_state = puzzle
        self.goal = tuple(
                        tuple( 
                            colonne + ligne * (len(puzzle)) + 1
                            if (ligne, colonne) != (len(puzzle) - 1, len(puzzle) - 1)
                            else self.EMPTY
                            for colonne in range(len(puzzle))
                        ) 
                     for ligne in range(len(puzzle))
                     )

        self._goal_positions = {
            col + row * len(puzzle) + 1
            if (row, col) != (len(puzzle) - 1, len(puzzle) - 1)
            else self.EMPTY
            :
            (row, col)
            for col in range(len(puzzle))
            for row in range(len(puzzle))
        }

        super().__init__(self.initial_state)

    def is_correct_position(self, value, row, col):
        gr, gc = self._goal_positions[value]

        return (row, col) == (gr, gc)

    def _find_symbol(self, symbol, state):
        for id_row, row in enumerate(state):
            for id_col, col in enumerate(row):
                if col == symbol:
                    return (id_row, id_col)

        raise ValueError( f"Symbole {symbol} introuvable dans le puzzle.")
    
    # A(s) : déplacements qui restent dans le puzzle et ne vont pas dans un mur
    def actions(self, state):
        row, col = self._find_symbol(self.EMPTY, state)
        legal_actions = []

        for action, (dr, dc) in self.MOVES.items():

            nr = row + dr
            nc = col + dc

            if 0 <= nr < len(state) and 0 <= nc < len(state):
                legal_actions.append(action)

        return legal_actions

    # RESULT(s, a)
    def result(self, state, action):
        puzzle_t = [list(ligne) for ligne in state]

        id_row_e, id_col_e = self._find_symbol(self.EMPTY, state)
        dr, dc = self.MOVES[action]
        id_row_s, id_col_s = (id_row_e + dr, id_col_e + dc)

        puzzle_t[id_row_e][id_col_e] = puzzle_t[id_row_s][id_col_s]
        puzzle_t[id_row_s][id_col_s] = self.EMPTY

        return tuple(tuple(row) for row in puzzle_t)


    def goal_test(self, state):
        return state == self.goal

    # c(s, a, s') : dépend de la case d'arrivée
    def step_cost(self, state, action, next_state):
        return 1

    # h(s) : somme des distances de Manhattan
    def heuristic(self, state):
        d = 0

        for id_row, row in enumerate(state):
            for id_col, col in enumerate(row):
                # ignore la case vide
                if col == self.EMPTY:
                    continue
                id_row_g, id_col_g = self._goal_positions[col]

                d += abs(id_row - id_row_g) + abs(id_col - id_col_g)

        return d

    # 'A' marque la position de l'agent
    def display(self, state):
        place_by_number = len(str(len(state) ** 2)) + 2
        for id_row, row in enumerate(state):
            print("-" * ( place_by_number * len(state) + len(state) - 1) )
            print("|", end=None)
            for id_col, col in enumerate(row):
                empty_place = place_by_number - len(str(col))
                print(" " * empty_place, end=None)
                print(col, end=None)
                print("|", end=None)
            print()
        print("-" * ( place_by_number * len(state) + len(state) - 1) )
