import heapq
import time

from .strategies import STRATEGIES


class Node:
    """Un noeud de l'arbre de recherche."""

    def __init__(self, state, parent, action, g, depth):
        self.state = state      # état du problème
        self.parent = parent    # noeud parent poiur le chemin
        self.action = action    # dernière action réalisée
        self.g = g              # coût du chemin depuis l'état initial
        self.depth = depth     


class Stats:
    def __init__(self):
        self.generated = 0      # noeuds ajoutés dans OPEN
        self.expanded = 0       # noeuds retirés de OPEN et développés
        self.max_open = 0       # taille maximale de OPEN
        self.time_s = 0.0


class Result:
    """
    status : "solution"    : un chemin a été trouvé
             "no_solution" : tout l'espace a été exploré, il n'y a pas de chemin
             "limit"       : arrêt de sécurité 
    """

    def __init__(self, status, stats, reason="", node=None):
        self.status = status
        self.stats = stats
        self.reason = reason    # raison de l'arrêt si status == "limit"
        self.actions = []
        self.states = []
        self.cost = 0
        self.depth = 0

        if node is not None:
            self.cost = node.g
            self.depth = node.depth

            # on remonte de la solution jusqu'à la racine
            while node is not None:
                self.states.insert(0, node.state)
                if node.parent is not None:
                    self.actions.insert(0, node.action)
                node = node.parent

    @property
    def solved(self):
        return self.status == "solution"


def SEARCH(problem, strategy="astar", mode="graph",
           max_expansions=500000, max_open=1000000, max_time=30):
    """

    strategy : clé de STRATEGIES ("bfs", "ucs", "greedy", "astar")
    mode     : "tree" , "graph"
    max_*    : garde-fous qui déclenchent l'état "limit"


    """

    f = STRATEGIES[strategy].priority           # définit la stratégie de recherche
    graph = (mode == "graph")
    stats = Stats()
    start_time = time.time()

    def fin(status, reason="", node=None):
        stats.time_s = time.time() - start_time
        return Result(status, stats, reason, node)

    root = Node(problem.initial_state, None, None, 0, 0)

    # OPEN est une file de priorité : heappop renvoie le plus petit tuple.
    # Le numéro départage les égalités de f (premier généré, premier sorti)

    numero = 0
    OPEN = [(f(root, problem), numero, root)]
    stats.generated = 1
    stats.max_open = 1

    # graph seulement : état -> plus petit g trouvé jusqu'ici
    best_g = {root.state: 0}

    while OPEN:
        _, _, node = heapq.heappop(OPEN)

        if graph and node.g > best_g[node.state]:
            continue

        if problem.goal_test(node.state):
            return fin("solution", node=node)

        if stats.expanded >= max_expansions:
            return fin("limit", f"max_expansions={max_expansions} atteint")
        if time.time() - start_time > max_time:
            return fin("limit", f"max_time={max_time}s atteint")

        stats.expanded += 1

        for action in problem.actions(node.state):
            next_state = problem.result(node.state, action)
            g = node.g + problem.step_cost(node.state, action, next_state)

            # graph : on abandonne un état déjà connu avec un coût meilleur ou égal
            if graph:
                if next_state in best_g and best_g[next_state] <= g:
                    continue
                best_g[next_state] = g

            child = Node(next_state, node, action, g, node.depth + 1)
            numero += 1
            heapq.heappush(OPEN, (f(child, problem), numero, child))
            stats.generated += 1

        stats.max_open = max(stats.max_open, len(OPEN))
        if len(OPEN) > max_open:
            return fin("limit", f"max_open={max_open} dépassé (mémoire)")

    # OPEN est vide : tout a été exploré sans trouver le but
    return fin("no_solution")
