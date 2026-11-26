"""Bouton d'options (roue crantée) + fenêtre modale de choix du thème."""
import math

import pygame

from . import theme as T
from .widgets import Button, Dropdown


class OptionsMenu:
    PANEL_W = 320
    PANEL_H = 230

    def __init__(self, pos=None, size=40):
        self.size = size
        self.pos = pos
        self.is_open = False
        self._built_for = None
        self.dropdown = None
        self.close_btn = None
        self.panel_rect = pygame.Rect(0, 0, 0, 0)

    # ---------- layout ----------
    def _gear_rect(self, surf):
        if self.pos is not None:
            return pygame.Rect(self.pos, (self.size, self.size))
        return pygame.Rect(surf.get_width() - self.size - 12, 12, self.size, self.size)

    def _build(self, surf):
        sw, sh = surf.get_size()
        if self._built_for == (sw, sh):
            return
        self._built_for = (sw, sh)

        self.panel_rect = pygame.Rect(0, 0, self.PANEL_W, self.PANEL_H)
        self.panel_rect.center = (sw // 2, sh // 2)
        p = self.panel_rect

        options = [(k, v["label"]) for k, v in T.THEMES.items()]
        self.dropdown = Dropdown(
            "Thème", p.x + 20, p.y + 70, p.w - 40,
            options, selected=T.current_theme,
            on_change=lambda key: T.set_theme(key),
        )
        self.close_btn = Button((p.x + 20, p.bottom - 58, p.w - 40, 38),
                                "Fermer", self.close)

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False
        if self.dropdown:
            self.dropdown.open = False

    # ---------- événements ----------
    def handle(self, ev, surf):
        """Renvoie True si l'événement est consommé."""
        self._build(surf)
        gear = self._gear_rect(surf)

        if not self.is_open:
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and gear.collidepoint(ev.pos):
                self.dropdown.selected = T.current_theme
                self.open()
                return True
            return False

        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            if self.dropdown.open:
                self.dropdown.open = False    # 1er Échap : ferme juste la liste
            else:
                self.close()
            return True

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.dropdown.open:
                self.dropdown.click(ev.pos)   # choix d'un thème ou fermeture de la liste
            elif not self.panel_rect.collidepoint(ev.pos):
                self.close()                  # clic en dehors = fermer
            elif not self.dropdown.click(ev.pos):
                self.close_btn.click(ev.pos)
            return True
        return ev.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION, pygame.KEYDOWN)

    # ---------- dessin ----------
    @staticmethod
    def _gear_points(cx, cy, r_out, r_in, teeth=8):
        """Contour d'un engrenage : dents trapézoïdales."""
        pts = []
        step = 2 * math.pi / teeth
        for i in range(teeth):
            a = i * step
            for frac, rad in ((-0.25, r_in), (-0.16, r_out), (0.16, r_out), (0.25, r_in), (0.5, r_in)):
                ang = a + frac * step
                pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
        return pts

    def _draw_gear(self, surf, rect):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        bg = T.PANEL_LIGHT if hover else T.PANEL

        # fond du bouton + contour qui s'allume au survol
        pygame.draw.rect(surf, bg, rect, border_radius=10)
        pygame.draw.rect(surf, T.ACCENT if hover else T.PANEL_LIGHT, rect, width=2, border_radius=10)

        cx, cy = rect.center
        r_out = rect.w * 0.34
        r_in = rect.w * 0.25
        color = T.ACCENT if hover else T.TEXT

        pts = self._gear_points(cx, cy, r_out, r_in)
        pygame.draw.polygon(surf, color, pts)
        pygame.draw.circle(surf, bg, (cx, cy), int(rect.w * 0.11))   # trou central

    def draw(self, surf):
        """À appeler en TOUT DERNIER dans la boucle de dessin."""
        self._build(surf)
        self._draw_gear(surf, self._gear_rect(surf))

        if not self.is_open:
            return

        veil = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 150))
        surf.blit(veil, (0, 0))

        p = self.panel_rect
        pygame.draw.rect(surf, T.BG, p, border_radius=14)
        pygame.draw.rect(surf, T.ACCENT, p, width=2, border_radius=14)
        T.draw_text(surf, "Options", (p.x + 20, p.y + 18), 32, T.TEXT, bold=True)

        self.dropdown.selected = T.current_theme
        self.close_btn.draw(surf)
        self.dropdown.draw(surf)              # en dernier : la liste recouvre « Fermer »