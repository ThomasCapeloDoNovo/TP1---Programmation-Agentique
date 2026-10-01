from problems import build
from src.agent import AGENT

# "gui"     : fenêtre pygame, tout se choisit dans le menu
# "console" : affichage texte, utilise les paramètres de la branche console
INTERFACE = "gui"


if INTERFACE == "gui":
    from interface.gui.app import launch
    launch()

else:           # Paramètres utilisés seulement en mode console.

    PROBLEM_TYPE = "maze"        # une clé de : problems/__init__.py
    INSTANCE = "facile"          # un nom de PROBLEMS[PROBLEM_TYPE] (ex. problems/mazes.py)
    STRATEGY = "astar"           # bfs, ucs, greedy, astar
    MODE = "graph"               # "graph" (mémorise les états vus) ou "tree" (aucune mémoire)

    problem = build(PROBLEM_TYPE, INSTANCE)

    result = AGENT(
        problem,
        strategy=STRATEGY,
        mode=MODE,
        pause=0.0               
    )
