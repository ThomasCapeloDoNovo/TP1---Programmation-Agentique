"""Petits widgets maison (aucune dépendance autre que pygame)."""
import pygame

from . import theme as T


class Button:
    def __init__(self, rect, label, callback=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.callback = callback

    def draw(self, surf, selected=False, enabled=True):
        hover = enabled and self.rect.collidepoint(pygame.mouse.get_pos())
        if not enabled:
            color = T.PANEL
        elif selected:
            color = T.ACCENT
        else:
            color = T.PANEL_LIGHT if hover else T.PANEL
        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        pygame.draw.rect(surf, T.ACCENT_DARK if selected else T.PANEL_LIGHT,
                         self.rect, width=2, border_radius=8)
        T.draw_text(surf, self.label, self.rect.center, 24,
                    T.TEXT if enabled else T.MUTED, center=True)

    def click(self, pos):
        if self.rect.collidepoint(pos):
            if self.callback:
                self.callback()
            return True
        return False


class Selector:
    """Une rangée d'options mutuellement exclusives."""

    def __init__(self, title, x, y, width, options, selected=None, on_change=None):
        self.title, self.x, self.y, self.width = title, x, y, width
        self.on_change = on_change
        self.selected = selected
        self.set_options(options)

    def set_options(self, options):
        """options : liste de (clé, libellé)."""
        self.options = list(options)
        if self.selected not in [k for k, _ in self.options] and self.options:
            self.selected = self.options[0][0]
        self.buttons, x, y = [], self.x, self.y + 28
        for key, label in self.options:
            w = max(90, T.font(24).size(label)[0] + 28)
            if x + w > self.x + self.width:
                x, y = self.x, y + 44
            self.buttons.append((key, Button((x, y, w, 38), label)))
            x += w + 10
        self.height = y + 38 - self.y

    def draw(self, surf):
        T.draw_text(surf, self.title, (self.x, self.y), 22, T.MUTED)
        for key, b in self.buttons:
            b.draw(surf, selected=(key == self.selected))

    def click(self, pos):
        for key, b in self.buttons:
            if b.rect.collidepoint(pos):
                if key != self.selected:
                    self.selected = key
                    if self.on_change:
                        self.on_change(key)
                return True
        return False
