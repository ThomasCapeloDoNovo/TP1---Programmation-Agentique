from src.problem import Problem
import math

class NavigationProblem(Problem) :
    """Navigation
    
    état : nom de la ville pù on se trouve
    coût : poids associé au chemin entre deux villes
    """

    def __init__(self, coords, roads, start, goal):
        self.name = "Navigation"
        self.coords = coords
        self.start = start          # conservé à part : initial_state peut être modifié par l'agent
        self.goal = goal

        #List des adjacences entre sommets
        self.graph = {city: {} for city in coords}
        for a, b, w in roads:
            self.graph[a][b] = w
            self.graph[b][a] = w
            if w < self._euclid(a, b):
                raise ValueError(f"Route {a}-{b} ({w}) plus courte que la ligne droite : "
                                 "l'heuristique ne serait plus admissible.")

        super().__init__(start)

    #Distance euclidienne entre deux villes
    def _euclid(self, a, b):
        (x1, y1), (x2, y2) = self.coords[a], self.coords[b]
        return math.hypot(x1 - x2, y1 - y2)

    # A(s) : on peut aller vers chaque ville voisine
    def actions(self, state):
        return sorted(self.graph[state])

    # RESULT(s, a) : l'action est directement la ville d'arrivée
    def result(self, state, action):
        return action

    def goal_test(self, state):
        return state == self.goal

    # c(s, a, s') : poids de la route
    def step_cost(self, state, action, next_state):
        return self.graph[state][next_state]

    # h(s) : distance à vol d'oiseau jusqu'au but
    def heuristic(self, state):
        return self._euclid(state, self.goal)

    # --- affichage console
    def display(self, state):
        print(f"Position : {state}\n")

    def display_solution(self, states):
        print("Itinéraire :", " -> ".join(states))