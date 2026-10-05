
from src.problem import Problem

class ArithProblem(Problem):
    """Arith.

    arith  : tuple (goal, tuple(valeurs), tuple(opération))
    état  : tuple de tuple (valeur, formule)
    coût  : 1 par case

    Pour changer les règles : actions() pour les déplacements autorisés (ex. step_cost() pour les coûts, heuristic() pour l'estimation.
    """

    def __init__(self, arith):
        self.puzzle = arith

        self.initial_state = tuple(
            (val, str(val))
            for val in arith[1]
        )
        self.goal = arith[0]

        super().__init__(self.initial_state)
    
    # A(s) : déplacements qui restent dans le puzzle et ne vont pas dans un mur
    def actions(self, state):
        # liste des actions liste de tuple(id_val1, id_val2, opération entre)
        legal_actions = []
        for id_val, val in enumerate(state):
            for id_val2, val2 in enumerate(state):
                if id_val2 <= id_val:
                    continue
                for ac in self.puzzle[2]:
                    if id_val != id_val2:
                        try:
                            # problème avec la division par 0, pas simple à prédire
                            res_str = f"({val[0]}) {ac} ({val2[0]})"
                            eval(res_str)
                            legal_actions.append((id_val, id_val2, ac))
                        except Exception as e:
                            continue

        return legal_actions

    # RESULT(s, a)
    def result(self, state, action):
        res_str = f"({state[action[0]][1]}) {action[2]} ({state[action[1]][1]})"
        res_fl = eval(res_str)

        arith = [list(ligne) for ligne in state]
        for id in sorted([action[0], action[1]], reverse=True):
            arith.pop(id)

        arith.append([res_fl, res_str])
        return tuple(tuple(row) for row in arith)


    def goal_test(self, state):
        return len(state) == 1 and state[0][0 ]== self.goal

    # c(s, a, s') : dépend de la case d'arrivée
    def step_cost(self, state, action, next_state):
        return 1

    # aucune idée
    def heuristic(self, state):
        # min de la val absolue ? rajouter ptet le nombre de chiffres restant pour l'encourager à tout utiliser
        return 0
        #sinon nombre d'opéaration restant si le coût reste à 1 -> len(state) -1, ça pue un peu sa mère franchement

    #
    def display(self, state):
        for s in state:
            print(s)
