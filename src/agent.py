import time

from .search import SEARCH
from .strategies import STRATEGIES



def PERCEIVE(problem, state):
    return state


def UPDATE_STATE(state, percept):
    return percept


def FORMULATE_GOAL(problem, state):
    return problem


def FORMULATE_PROBLEM(problem, state, goal):
    # Même problème, mais l'état initial devient l'état courant de l'agent.
    # (Modifie l'objet problem reçu.)
    problem.initial_state = state
    return problem


def EXECUTE(problem, state, action):
    return problem.result(state, action)

# +100 en arrivant pour un labyrinthe, à voir si à adapter pour les autres problèmes
def PERFORMANCE(problem, previous_state, action, state):
    if problem.goal_test(state):
        return 100

    return -problem.step_cost(previous_state, action, state)


def LEARN(state, action, percept):
    return state


def AFFICHER_RESULTAT(result):
    """Affiche le statut et les statistiques d'un Result (voir SEARCH)."""
    stats = result.stats

    if result.status == "solution":
        print(f"Solution trouvée ! Coût = {result.cost} | Profondeur = {result.depth}")
    elif result.status == "no_solution":
        print("Aucune solution : tout l'espace d'états a été exploré.")
    else:
        print(f"Arrêt de sécurité : {result.reason}")

    print(
        f"Noeuds générés : {stats.generated} | "
        f"expansés : {stats.expanded} | "
        f"max OPEN : {stats.max_open} | "
        f"temps : {stats.time_s:.3f} s"
    )


def AGENT(problem, strategy="astar", mode="graph", pause=0.0):
    """

    problem  : un Problem (labyrinth pour l'instant)
    strategy : clé de STRATEGIES
    mode     : "graph" ou "tree"
    pause    : secondes d'attente entre deux actions pour l'affichage

    Retourne {"success": bool, "state": état final, "steps": nombre d'actions, "score": int}.
    """

    state = problem.initial_state
    plan = []

    score = 0
    steps = 0

    print("=== AUSSI V2.0 ===")
    print(f"SEARCH : {STRATEGIES[strategy].name} | {mode}-search")
    print()

    problem.display(state)

    while not problem.goal_test(state):

        percept = PERCEIVE(problem, state)
        state = UPDATE_STATE(state, percept)

        # plus de plan : l'agent en cherche un
        if not plan:

            goal = FORMULATE_GOAL(problem, state)

            current_problem = FORMULATE_PROBLEM(
                problem,
                state,
                goal
            )

            result = SEARCH(current_problem, strategy, mode)

            AFFICHER_RESULTAT(result)
            print()

            if not result.solved:
                return {
                    "success": False,
                    "state": state,
                    "steps": steps,
                    "score": score
                }

            plan = list(result.actions)
            print("Plan trouvé :", plan)
            print()

        action = plan.pop(0)

        previous_state = state

        state = EXECUTE(
            problem,
            state,
            action
        )

        steps += 1

        score += PERFORMANCE(
            problem,
            previous_state,
            action,
            state
        )

        state = LEARN(
            state,
            action,
            percept
        )

        print(
            f"Étape {steps:3d} | "
            f"Action : {action:7s} | "
            f"État : {state} | "
            f"Score : {score}"
        )

        problem.display(state)

        if pause > 0:
            time.sleep(pause)

    print("AUSSI a atteint le but!")
    print(f"Nombre d'étapes : {steps}")
    print(f"Score final : {score}")

    return {
        "success": True,
        "state": state,
        "steps": steps,
        "score": score
    }
