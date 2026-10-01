from src.strategies import STRATEGIES


def print_result(problem, result, strategy, mode):
    s = result.stats
    print(f"\n=== {problem.name} | {STRATEGIES[strategy].name} | {mode}-search ===")
    if result.solved:
        print(f"Solution trouvée ! coût = {result.cost:g} | profondeur = {result.depth}")
        print("Plan :", result.actions)
        problem.display_solution(result.states)
    elif result.status == "no_solution":
        print("Aucune solution : l'espace d'états a été entièrement exploré.")
    else:
        print(f"Arrêt de sécurité : {result.reason}")
    print(f"Noeuds générés : {s.generated} | expansés : {s.expanded} | "
          f"max OPEN : {s.max_open} | temps : {s.time_s:.3f} s")
