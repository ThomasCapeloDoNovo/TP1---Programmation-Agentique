"""Dessin des problèmes. Les problèmes (src/problems) ne connaissent pas pygame :
on associe ici chaque type de problème à un Renderer.

Pour un nouveau problème : écrire un Renderer et l'ajouter à RENDERERS.
draw(surf, rect, problem, state, path) :
  state : état à montrer (position de l'agent ou état final)
  path  : liste d'états de la solution (ou du trajet de l'agent)
"""
import pygame

from problems.maze import MazeProblem
from . import theme as T


class Renderer:
    def draw(self, surf, rect, problem, state, path):
        raise NotImplementedError


class GenericRenderer(Renderer):
    """Secours : affiche simplement l'état en texte."""

    def draw(self, surf, rect, problem, state, path):
        pygame.draw.rect(surf, T.PANEL, rect, border_radius=10)
        for i, line in enumerate(T.wrap_text(f"État : {state}", 28, rect.w - 30)):
            T.draw_text(surf, line, (rect.x + 15, rect.y + 15 + i * 26), 28)


class MazeRenderer(Renderer):
    def draw(self, surf, rect, problem, state, path):
        rows, cols = len(problem.maze), max(len(r) for r in problem.maze)
        cell = int(min(rect.w / cols, rect.h / rows))
        ox = rect.x + (rect.w - cell * cols) // 2
        oy = rect.y + (rect.h - cell * rows) // 2
        big = cell >= 22

        pygame.draw.rect(surf, (30, 34, 44), (ox, oy, cell * cols, cell * rows))
        for r, row in enumerate(problem.maze):
            for c, ch in enumerate(row):
                cr = pygame.Rect(ox + c * cell, oy + r * cell, cell, cell)
                if ch == problem.WALL:
                    pygame.draw.rect(surf, (30, 34, 44), cr)
                    continue
                if ch.isdigit():                      # terrain coûteux : plus foncé
                    k = (int(ch) - 1) / 8
                    color = (int(225 - 95 * k), int(215 - 120 * k), int(180 - 130 * k))
                else:
                    color = (232, 232, 236)
                pygame.draw.rect(surf, color, cr)
                if ch.isdigit() and big:
                    T.draw_text(surf, ch, cr.center, int(cell * 0.6), (60, 40, 20), center=True)
                pygame.draw.rect(surf, (200, 200, 208), cr, width=1)

        # solution / trajet
        if path and len(path) > 1:
            pts = [(ox + c * cell + cell // 2, oy + r * cell + cell // 2) for r, c in path]
            pygame.draw.lines(surf, T.WARN, False, pts, max(3, cell // 6))

        # départ et but
        for sym, color in ((problem.START, T.GOOD), (problem.GOAL, T.BAD)):
            for r, row in enumerate(problem.maze):
                for c, ch in enumerate(row):
                    if ch == sym:
                        cr = pygame.Rect(ox + c * cell, oy + r * cell, cell, cell).inflate(-4, -4)
                        pygame.draw.rect(surf, color, cr, border_radius=6)
                        T.draw_text(surf, sym, cr.center, max(16, int(cell * 0.7)),
                                    (20, 20, 20), bold=True, center=True)

        # agent / noeud courant
        if state is not None:
            r, c = state
            center = (ox + c * cell + cell // 2, oy + r * cell + cell // 2)
            pygame.draw.circle(surf, T.ACCENT, center, max(5, cell // 3))
            pygame.draw.circle(surf, (255, 255, 255), center, max(5, cell // 3), 2)


RENDERERS = [
    (MazeProblem, MazeRenderer()),
    # (NavigationProblem, NavigationRenderer()),  <- à ajouter avec chaque nouveau problème
]


def get_renderer(problem):
    for cls, renderer in RENDERERS:
        if isinstance(problem, cls):
            return renderer
    return GenericRenderer()
