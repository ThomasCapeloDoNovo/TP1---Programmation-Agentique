from src.problem import Problem


class MazeProblem(Problem):
    """Labyrinthe.

    maze  : liste de chaînes, une par ligne
    état  : (ligne, colonne) de l'agent
    coût  : 1 par case, ou le chiffre de la case d'arrivée si c'est un terrain coûteux (2 à 9 pour les pièges par exemple)

    Pour changer les règles : actions() pour les déplacements autorisés (ex. step_cost() pour les coûts, heuristic() pour l'estimation.
    """

    WALL = "#"
    START = "S"
    GOAL = "G"

    MOVES = {
        "HAUT": (-1, 0),
        "BAS": (1, 0),
        "GAUCHE": (0, -1),
        "DROITE": (0, 1),
    }

    def __init__(self, maze):
        self.maze = maze

        self.initial_state = self._find_symbol(self.START)
        self.goal = self._find_symbol(self.GOAL)

        super().__init__(self.initial_state)


    def _find_symbol(self, symbol):
        for row in range(len(self.maze)):
            for col in range(len(self.maze[row])):

                if self.maze[row][col] == symbol:
                    return (row, col)

        raise ValueError( f"Symbole {symbol} introuvable dans le labyrinthe.")

    # A(s) : déplacements qui restent dans le labyrinthe et ne vont pas dans un mur
    def actions(self, state):
        row, col = state
        legal_actions = []

        for action, (dr, dc) in self.MOVES.items():

            nr = row + dr
            nc = col + dc

            if 0 <= nr < len(self.maze) and 0 <= nc < len(self.maze[nr]):
                if self.maze[nr][nc] != self.WALL:
                    legal_actions.append(action)

        return legal_actions

    # RESULT(s, a)
    def result(self, state, action):
        row, col = state
        dr, dc = self.MOVES[action]

        return ( row + dr, col + dc )


    def goal_test(self, state):
        return state == self.goal

    # c(s, a, s') : dépend de la case d'arrivée
    def step_cost(self, state, action, next_state):
        row, col = next_state
        case = self.maze[row][col]

        if case.isdigit():
            return int(case)

        return 1

    # h(s) : distance de Manhattan, admissible tant que chaque déplacement coûte au moins 1 
    def heuristic(self, state):
        row, col = state
        goal_row, goal_col = self.goal

        return ( abs(row - goal_row) + abs(col - goal_col))

    # 'A' marque la position de l'agent
    def display(self, state):
        agent_row, agent_col = state

        for row in range(len(self.maze)):
            line = ""

            for col in range(len(self.maze[row])):

                if (row, col) == (agent_row, agent_col):
                    line += "A"
                else:
                    line += self.maze[row][col]

            print(line)

        print()
