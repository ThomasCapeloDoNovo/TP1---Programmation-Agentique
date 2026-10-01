"""Interface pygame centralisée.

MenuScreen : choix du problème, de l'instance, de la stratégie et du mode de
recherche (tree/graph).
RunScreen  : lance le calcul (dans un thread) puis affiche le résultat :
             le plateau, les statistiques et le détail des actions réalisées.

L'interface ne dépend d'aucun problème précis : elle passe par le registre
PROBLEMS et par les Renderers (renderers.py).
"""
import threading
import time

import pygame

from src.search import SEARCH
from src.strategies import STRATEGIES
from problems import PROBLEMS, PROBLEM_LABELS, build
from . import theme as T
from .renderers import get_renderer
from .widgets import Button, Selector

W, H = 1100, 720
LIMITS = dict(max_expansions=300_000, max_time=10.0)
ROW_H = 24


def fit_text(text, size, max_width):
    """Tronque le texte avec '…' pour qu'il tienne dans max_width pixels."""
    text, f = str(text), T.font(size)
    if f.size(text)[0] <= max_width:
        return text
    while text and f.size(text + "…")[0] > max_width:
        text = text[:-1]
    return text + "…"


class MenuScreen:
    def __init__(self, app):
        self.app = app
        x, w = 60, W - 120
        self.problem = Selector("Problème", x, 110, w,
                                [(k, PROBLEM_LABELS.get(k, k.title())) for k in PROBLEMS],
                                on_change=self._problem_changed)
        self.instance = Selector("Instance", x, 200, w, [])
        self.strategy = Selector("Stratégie", x, 290, w,
                                 [(k, s.name) for k, s in STRATEGIES.items()], "astar")
        self.mode = Selector("Mode de recherche", x, 380, w,
                             [("graph", "Graph-Search"), ("tree", "Tree-Search")], "graph")
        self.selectors = [self.problem, self.instance, self.strategy, self.mode]
        self.launch = Button((x, 490, 240, 52), "Lancer", self.start)
        self._problem_changed(self.problem.selected)

    def _problem_changed(self, key):
        self.instance.set_options([(k, k.replace("_", " ")) for k in PROBLEMS[key]])

    def start(self):
        self.app.screen_obj = RunScreen(self.app, self.problem.selected, self.instance.selected,
                                        self.strategy.selected, self.mode.selected)

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for s in self.selectors:
                s.click(ev.pos)
            self.launch.click(ev.pos)
        elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.start()

    def update(self, dt):
        pass

    def draw(self, surf):
        surf.fill(T.BG)
        T.draw_text(surf, "AUSSI V2.0", (60, 30), 54, T.ACCENT, bold=True)
        T.draw_text(surf, "Agent Universel de Support Super Intelligent", (60, 75), 26, T.MUTED)
        for s in self.selectors:
            s.draw(surf)
        self.launch.draw(surf)
        T.draw_text(surf, "Entrée : lancer", (320, 504), 22, T.MUTED)


class RunScreen:
    BOARD = pygame.Rect(20, 80, 680, 620)
    PANEL = pygame.Rect(720, 80, 360, 620)

    def __init__(self, app, ptype, instance, strategy, mode):
        self.app = app
        self.ptype, self.instance, self.strategy, self.mode = ptype, instance, strategy, mode
        self.problem = build(ptype, instance)
        self.renderer = get_renderer(self.problem)

        self.done = False
        self.error = None
        self.result = None       # SearchResult
        self.rows = []           # détail des actions (construit après le calcul)
        self.scroll = 0          # premier élément visible de la liste
        self.list_rect = None    # zone de la liste (fixée au dessin)
        self.menu_btn = Button((W - 190, 22, 170, 40), "Menu (Échap)", self.back)

        # le thread démarre en dernier : tout l'état doit être initialisé avant
        self.t0 = time.perf_counter()
        threading.Thread(target=self._work, daemon=True).start()

    # ---------- calcul (thread) ----------
    def _work(self):
        try:
            self.result = SEARCH(self.problem, self.strategy, self.mode, **LIMITS)
            if self.result.solved:
                self.rows = self._build_rows(self.result)
        except Exception as exc:  # affichage propre plutôt qu'un plantage
            self.error = repr(exc)
        self.done = True

    def _build_rows(self, r):
        """Une ligne par action : (libellé, état atteint, coût de l'action, coût cumulé)."""
        rows = [("Départ", r.states[0], None, 0)]
        g = 0
        for i, action in enumerate(r.actions):
            s0, s1 = r.states[i], r.states[i + 1]
            c = self.problem.step_cost(s0, action, s1)
            g += c
            rows.append((f"{i + 1}. {action}", s1, c, g))
        return rows

    def back(self):
        self.app.screen_obj = MenuScreen(self.app)

    # ---------- événements ----------
    def _visible(self):
        return max(1, self.list_rect.h // ROW_H) if self.list_rect else 1

    def _scroll_by(self, delta):
        max_scroll = max(0, len(self.rows) - self._visible())
        self.scroll = max(0, min(max_scroll, self.scroll + delta))

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.menu_btn.click(ev.pos)
        elif ev.type == pygame.MOUSEWHEEL:
            self._scroll_by(-ev.y * 3)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                self.back()
            elif ev.key == pygame.K_UP:
                self._scroll_by(-1)
            elif ev.key == pygame.K_DOWN:
                self._scroll_by(1)
            elif ev.key == pygame.K_PAGEUP:
                self._scroll_by(-self._visible())
            elif ev.key == pygame.K_PAGEDOWN:
                self._scroll_by(self._visible())
            elif ev.key == pygame.K_HOME:
                self.scroll = 0
            elif ev.key == pygame.K_END:
                self._scroll_by(len(self.rows))

    def update(self, dt):
        pass

    # ---------- dessin ----------
    def draw(self, surf):
        surf.fill(T.BG)
        title = (f"{PROBLEM_LABELS.get(self.ptype, self.ptype)} / {self.instance.replace('_', ' ')}"
                 f"  |  {STRATEGIES[self.strategy].name}  |  {self.mode}-search")
        T.draw_text(surf, title, (20, 30), 32, T.TEXT, bold=True)
        self.menu_btn.draw(surf)
        pygame.draw.rect(surf, T.PANEL, self.BOARD, border_radius=10)
        pygame.draw.rect(surf, T.PANEL, self.PANEL, border_radius=10)

        if not self.done:
            T.draw_text(surf, f"Recherche en cours… {time.perf_counter() - self.t0:.1f} s",
                        self.BOARD.center, 34, T.MUTED, center=True)
            return
        if self.error:
            T.draw_text(surf, "Erreur : " + self.error, (self.BOARD.x + 20, self.BOARD.y + 20), 26, T.BAD)
            return

        self._draw_panel(surf)
        self._draw_board(surf)

    def _draw_board(self, surf):
        r = self.result
        path = r.states if r.solved else []
        state = path[-1] if path else self.problem.initial_state
        hovered = self._hovered_row()
        if hovered is not None:               # survol d'une action : montre où elle mène
            state = self.rows[hovered][1]
        self.renderer.draw(surf, self.BOARD.inflate(-20, -20), self.problem, state, path)

    def _hovered_row(self):
        if not self.list_rect or not self.rows:
            return None
        mx, my = pygame.mouse.get_pos()
        if not self.list_rect.collidepoint(mx, my):
            return None
        i = self.scroll + (my - self.list_rect.y) // ROW_H
        return i if 0 <= i < len(self.rows) else None

    def _draw_panel(self, surf):
        r, x, y = self.result, self.PANEL.x + 18, self.PANEL.y + 14
        w = self.PANEL.w - 36

        def line(label, value):
            nonlocal y
            T.draw_text(surf, label, (x, y), 21, T.MUTED)
            img = T.font(24, True).render(str(value), True, T.TEXT)
            surf.blit(img, (x + w - img.get_width(), y - 2))
            y += 27

        # statut
        if r.solved:
            T.draw_text(surf, "Solution trouvée", (x, y), 30, T.GOOD, bold=True)
        elif r.status == "no_solution":
            T.draw_text(surf, "Aucune solution", (x, y), 30, T.BAD, bold=True)
        else:
            T.draw_text(surf, "Arrêt de sécurité", (x, y), 30, T.WARN, bold=True)
        y += 36
        if r.status == "limit":
            for ln in T.wrap_text(r.reason, 21, w):
                T.draw_text(surf, ln, (x, y), 21, T.WARN)
                y += 21
            y += 6
        elif r.status == "no_solution":
            for ln in T.wrap_text("L'espace d'états a été entièrement exploré.", 21, w):
                T.draw_text(surf, ln, (x, y), 21, T.MUTED)
                y += 21
            y += 6

        s = r.stats
        if r.solved:
            line("Coût", f"{r.cost:g}")
            line("Profondeur", r.depth)
        line("Noeuds générés", s.generated)
        line("Noeuds expansés", s.expanded)
        line("Taille max OPEN", s.max_open)
        line("Temps", f"{s.time_s:.3f} s")

        if r.solved:
            self._draw_actions(surf, x, y + 10, w)

    def _draw_actions(self, surf, x, y, w):
        T.draw_text(surf, f"Actions réalisées ({len(self.rows) - 1})", (x, y), 24, T.TEXT, bold=True)
        T.draw_text(surf, "molette : défiler", (x + w - T.font(19).size("molette : défiler")[0], y + 4), 19, T.MUTED)
        y += 30
        self.list_rect = pygame.Rect(x - 6, y, w + 12, self.PANEL.bottom - y - 12)
        visible = self._visible()
        self._scroll_by(0)                    # garde le défilement valide
        hovered = self._hovered_row()

        for k, row in enumerate(self.rows[self.scroll:self.scroll + visible]):
            label, state, cost, g = row
            ry = self.list_rect.y + k * ROW_H
            if self.scroll + k == hovered:
                pygame.draw.rect(surf, T.PANEL_LIGHT, (self.list_rect.x, ry, self.list_rect.w, ROW_H),
                                 border_radius=5)
            right = "" if cost is None else f"+{cost:g} = {g:g}"
            rimg = T.font(20).render(right, True, T.GOOD if cost is not None else T.MUTED)
            surf.blit(rimg, (self.list_rect.right - rimg.get_width() - 12, ry + 4))
            T.draw_text(surf, label, (x, ry + 4), 20, T.TEXT)
            left_w = T.font(20).size(label)[0]
            avail = self.list_rect.w - left_w - rimg.get_width() - 50
            T.draw_text(surf, fit_text(state, 20, max(avail, 0)), (x + left_w + 14, ry + 4), 20, T.MUTED)

        if len(self.rows) > visible:          # barre de défilement
            track = pygame.Rect(self.list_rect.right - 5, self.list_rect.y, 4, self.list_rect.h)
            pygame.draw.rect(surf, T.PANEL_LIGHT, track, border_radius=2)
            th = max(24, int(track.h * visible / len(self.rows)))
            ty = track.y + int((track.h - th) * self.scroll / (len(self.rows) - visible))
            pygame.draw.rect(surf, T.ACCENT, (track.x, ty, track.w, th), border_radius=2)


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("AUSSI V2.0")
        self.surface = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        self.screen_obj = MenuScreen(self)
        self.running = True

    def step(self, dt):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            else:
                self.screen_obj.handle(ev)
        self.screen_obj.update(dt)
        self.screen_obj.draw(self.surface)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.step(self.clock.tick(60) / 1000)
        pygame.quit()


def launch():
    App().run()
