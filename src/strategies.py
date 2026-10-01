# Pour ajouter une stratégie :
#   1. écrire une fonction f_xxx(node, problem)
#   2. l'ajouter dans STRATEGIES (la clé est le nom utilisé dans main.py et le menu)


class Strategy:
    def __init__(self, name, priority):
        self.name = name            # nom affiché dans l'interface
        self.priority = priority    # fonction f(node, problem)


def f_bfs(node, problem):
    return node.depth


def f_ucs(node, problem):
    return node.g


def f_greedy(node, problem):
    return problem.heuristic(node.state)


def f_astar(node, problem):
    return node.g + problem.heuristic(node.state)


STRATEGIES = {
    "bfs": Strategy("BFS", f_bfs),
    "ucs": Strategy("UCS", f_ucs),
    "greedy": Strategy("Greedy", f_greedy),
    "astar": Strategy("A*", f_astar),
}
