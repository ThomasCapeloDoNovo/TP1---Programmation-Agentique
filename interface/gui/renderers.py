"""Dessin des problèmes. Les problèmes (src/problems) ne connaissent pas pygame :
on associe ici chaque type de problème à un Renderer.

Pour un nouveau problème : écrire un Renderer et l'ajouter à RENDERERS.
draw(surf, rect, problem, state, path) :
  state : état à montrer (position de l'agent ou état final)
  path  : liste d'états de la solution (ou du trajet de l'agent)
"""
import pygame

from problems.maze import MazeProblem
from problems.npuzzle import NPuzzleProblem
from problems.ariths import ArithProblem
from problems.navigation import NavigationProblem
from . import theme as T

from sympy.parsing.sympy_parser import parse_expr


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


class NPuzzleRenderer(Renderer):

    def draw(self, surf, rect, problem, state, path):

        n = len(state)

        cell = int(min(rect.w / n, rect.h / n))
        ox = rect.x + (rect.w - cell * n) // 2
        oy = rect.y + (rect.h - cell * n) // 2

        for r in range(n):
            for c in range(n):

                value = state[r][c]

                cr = pygame.Rect(
                    ox + c * cell,
                    oy + r * cell,
                    cell,
                    cell
                )

                if value == problem.EMPTY:

                    pygame.draw.rect(
                        surf,
                        (55, 60, 75),
                        cr.inflate(-6, -6),
                        border_radius=8
                    )

                else:
                    correct = problem.is_correct_position(value, r, c)

                    color = (
                        (180, 220, 180)
                        if correct else
                        (230, 230, 235)
                    )

                    pygame.draw.rect(
                        surf,
                        color,
                        cr.inflate(-6, -6),
                        border_radius=8
                    )

                    T.draw_text(
                        surf,
                        str(value),
                        cr.center,
                        max(20, int(cell * 0.45)),
                        (20, 20, 20),
                        bold=True,
                        center=True
                    )

class ArithRenderer(Renderer):

    def draw(self, surf, rect, problem, state, path):

        pygame.draw.rect(
            surf,
            T.PANEL,
            rect,
            border_radius=10
        )

        card_h = 90
        gap = 12

        total_h = len(state) * (card_h + gap) - gap

        oy = rect.y + max(20, (rect.h - total_h) // 2)

        for i, (value, expr) in enumerate(state):

            expr_aff = parse_expr(expr, evaluate=False)

            card = pygame.Rect(
                rect.x + 20,
                oy + i * (card_h + gap),
                rect.w - 40,
                card_h
            )

            pygame.draw.rect(
                surf,
                T.PANEL_LIGHT,
                card,
                border_radius=8
            )

            pygame.draw.rect(
                surf,
                T.ACCENT,
                card,
                width=2,
                border_radius=8
            )

            # expression
            T.draw_text(
                surf,
                expr_aff,
                (card.x + 12, card.y + 14),
                22,
                T.TEXT
            )

            # résultat
            T.draw_text(
                surf,
                f"= {value:g}",
                (card.x + 12, card.y + 50),
                24,
                T.GOOD,
                bold=True
            )


class NavigationRenderer(Renderer):
    def draw(self, surf, rect, problem, state, path):
        xs = [x for x, _ in problem.coords.values()]
        ys = [y for _, y in problem.coords.values()]
        margin = 60

        def to_px(city):
            """Coordonnées (km) -> pixels. y est inversé : le nord est en haut."""
            x, y = problem.coords[city]
            px = rect.x + margin + (x - min(xs)) / ((max(xs) - min(xs)) or 1) * (rect.w - 2 * margin)
            py = rect.y + margin + (max(ys) - y) / ((max(ys) - min(ys)) or 1) * (rect.h - 2 * margin)
            return int(px), int(py)

        # routes + poids (chaque route une seule fois)
        seen = set()
        for a, neighbors in problem.graph.items():
            for b, w in neighbors.items():
                if (b, a) in seen:
                    continue
                seen.add((a, b))
                pa, pb = to_px(a), to_px(b)
                pygame.draw.line(surf, (90, 98, 115), pa, pb, 3)
                mid = ((pa[0] + pb[0]) // 2, (pa[1] + pb[1]) // 2)
                T.draw_text(surf, f"{w:g}", mid, 20, T.MUTED, center=True)

        # itinéraire
        if len(path) > 1:
            pygame.draw.lines(surf, T.WARN, False, [to_px(c) for c in path], 6)

        # villes : départ vert, but rouge, position courante en bleu
        for city in problem.coords:
            if city == problem.start:
                color = T.GOOD
            elif city == problem.goal:
                color = T.BAD
            else:
                color = T.PANEL_LIGHT
            p = to_px(city)
            pygame.draw.circle(surf, color, p, 14)
            pygame.draw.circle(surf, T.TEXT, p, 14, 2)
            T.draw_text(surf, city, (p[0], p[1] + 26), 22, T.TEXT, center=True)

        if state is not None:
            pygame.draw.circle(surf, T.ACCENT, to_px(state), 8)


RENDERERS = [
    (MazeProblem, MazeRenderer()),
    (NPuzzleProblem, NPuzzleRenderer()),
    (ArithProblem, ArithRenderer()),
    (NavigationProblem, NavigationRenderer()),
    # (NavigationProblem, NavigationRenderer()),  <- à ajouter avec chaque nouveau problème
    ]


def get_renderer(problem):
    for cls, renderer in RENDERERS:
        if isinstance(problem, cls):
            return renderer
    return GenericRenderer()
