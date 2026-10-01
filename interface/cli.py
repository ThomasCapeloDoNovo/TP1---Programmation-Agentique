"""Point d'entrée des interfaces.

run_request() est la SEULE porte d'entrée vers le moteur : la GUI pygame, la
ligne de commande et (plus tard) un LLM passent tous par la même logique.
"""
import argparse

from src.search import SEARCH
from src.strategies import STRATEGIES
from problems import PROBLEMS, build
from .report import print_result


def run_request(problem_type, instance, strategy, mode, **limits):
    problem = build(problem_type, instance)
    result = SEARCH(problem, strategy, mode, **limits)
    print_result(problem, result, strategy, mode)
    return result


def main():
    ap = argparse.ArgumentParser(description="AUSSI V0")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("gui", help="interface pygame (défaut)")
    sv = sub.add_parser("solve", help="résoudre en console")
    sv.add_argument("-p", "--problem", default="maze", choices=PROBLEMS)
    sv.add_argument("-i", "--instance", default="facile")
    sv.add_argument("-s", "--strategy", default="astar", choices=STRATEGIES)
    sv.add_argument("-m", "--mode", default="graph", choices=["tree", "graph"])
    a = ap.parse_args()
    if a.cmd == "solve":
        run_request(a.problem, a.instance, a.strategy, a.mode)
    else:
        from .gui.app import launch   # import tardif : pygame requis seulement pour la GUI
        launch()
