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

class VerticalSelector(Selector):

    def set_options(self, options):
        self.options = list(options)

        if self.selected not in [k for k, _ in self.options] and self.options:
            self.selected = self.options[0][0]

        self.buttons = []
        y = self.y + 28

        for key, label in self.options:
            self.buttons.append(
                (key, Button((self.x, y, self.width, 38), label))
            )
            y += 44

        self.height = y - self.y
        
class NumberInput:
    """Sélecteur numérique avec boutons - et +, bornes et valeur par défaut."""
    def __init__(
        self,
        title,
        x,
        y,
        width,
        default_value=1,
        min_value=1,
        max_value=None,
        allow_float=False
    ):
        self.title = title
        self.rect = pygame.Rect(x, y + 28, width, 38)
        self.default_value = float(default_value) if allow_float else int(default_value)
        self.value = self.default_value
        self.min_value = min_value
        self.max_value = max_value
        self.allow_float = allow_float
        self.active = False
        self.minus_rect = pygame.Rect(self.rect.x, self.rect.y, 32, self.rect.height)
        self.plus_rect = pygame.Rect(self.rect.right - 32, self.rect.y, 32, self.rect.height)

    def handle(self, ev):
        if ev.type != pygame.MOUSEBUTTONDOWN or ev.button != 1:
            return
        if self.minus_rect.collidepoint(ev.pos):
            self.value = max(self.min_value, self.value - 1)
            self.active = False
        elif self.plus_rect.collidepoint(ev.pos):
            next_value = self.value + 1
            if self.max_value is None or next_value <= self.max_value:
                self.value = next_value
            self.active = False

    def validate(self):
        """Garantit une valeur valide ; sinon rétablit la valeur par défaut."""
        try:
            value = float(self.value) if self.allow_float else int(self.value)
            if value < self.min_value or (self.max_value is not None and value > self.max_value):
                raise ValueError
            self.value = value
        except (ValueError, TypeError, OverflowError):
            self.value = self.default_value
        return self.value

    @property
    def int_value(self):
        return int(self.validate())

    @property
    def float_value(self):
        return float(self.validate())

    def draw(self, surf):
        T.draw_text(surf, self.title, (self.rect.x, self.rect.y - 28), 22, T.MUTED)
        pygame.draw.rect(surf, T.PANEL, self.rect, border_radius=8)
        pygame.draw.rect(surf, T.PANEL_LIGHT, self.rect, width=2, border_radius=8)

        # Boutons moins et plus
        for button_rect, label in ((self.minus_rect, "-"), (self.plus_rect, "+")):
            pygame.draw.rect(surf, T.PANEL_LIGHT, button_rect, border_radius=6)
            T.draw_text(surf, label, button_rect.center, 25, T.TEXT, center=True)

        T.draw_text(surf, str(self.value), self.rect.center, 22, T.TEXT, center=True)

