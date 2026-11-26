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

class Dropdown:
    """Menu déroulant. La liste se déploie vers le bas par-dessus le reste."""
    ITEM_H = 38

    def __init__(self, title, x, y, width, options, selected=None, on_change=None):
        self.title, self.x, self.y, self.width = title, x, y, width
        self.options = list(options)              # liste de (clé, libellé)
        self.selected = selected if selected is not None else (self.options[0][0] if self.options else None)
        self.on_change = on_change
        self.open = False
        self.rect = pygame.Rect(x, y + 28, width, self.ITEM_H)
        self.height = 28 + self.ITEM_H

    def _item_rect(self, i):
        return pygame.Rect(self.rect.x, self.rect.bottom + 4 + i * self.ITEM_H,
                           self.rect.w, self.ITEM_H)

    def _list_rect(self):
        return pygame.Rect(self.rect.x, self.rect.bottom + 4,
                           self.rect.w, self.ITEM_H * len(self.options))

    def _label(self, key):
        return next((lbl for k, lbl in self.options if k == key), "")

    def click(self, pos):
        """Renvoie True si le clic a été consommé."""
        if self.open:
            for i, (key, _) in enumerate(self.options):
                if self._item_rect(i).collidepoint(pos):
                    if key != self.selected:
                        self.selected = key
                        if self.on_change:
                            self.on_change(key)
                    self.open = False
                    return True
            # clic ailleurs : on referme (et on consomme si c'était sur l'en-tête)
            was_header = self.rect.collidepoint(pos)
            self.open = False
            return was_header
        if self.rect.collidepoint(pos):
            self.open = True
            return True
        return False

    def _text_y(self, rect, size=24):
        """y du coin haut-gauche pour centrer verticalement un texte dans rect."""
        return rect.centery - T.font(size).get_height() // 2

    def draw_header(self, surf):
        T.draw_text(surf, self.title, (self.x, self.y), 22, T.MUTED)
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(surf, T.PANEL_LIGHT if hover else T.PANEL, self.rect, border_radius=8)
        pygame.draw.rect(surf, T.ACCENT if self.open else T.PANEL_LIGHT,
                         self.rect, width=2, border_radius=8)
        T.draw_text(surf, self._label(self.selected),
                    (self.rect.x + 14, self._text_y(self.rect)), 24, T.TEXT)
        # petite flèche (triangle)
        cx, cy = self.rect.right - 20, self.rect.centery
        pts = [(cx - 6, cy + 3), (cx + 6, cy + 3), (cx, cy - 4)] if self.open \
            else [(cx - 6, cy - 3), (cx + 6, cy - 3), (cx, cy + 4)]
        pygame.draw.polygon(surf, T.TEXT, pts)

    def draw_list(self, surf):
        """À dessiner en dernier pour passer au-dessus des autres éléments."""
        if not self.open:
            return
        lst = self._list_rect()
        pygame.draw.rect(surf, T.PANEL, lst, border_radius=8)
        mouse = pygame.mouse.get_pos()
        for i, (key, label) in enumerate(self.options):
            r = self._item_rect(i)
            if r.collidepoint(mouse):
                pygame.draw.rect(surf, T.PANEL_LIGHT, r.inflate(-6, -4), border_radius=6)
            elif key == self.selected:
                pygame.draw.rect(surf, T.ACCENT_DARK, r.inflate(-6, -4), border_radius=6)
            T.draw_text(surf, label, (r.x + 14, self._text_y(r)), 24, T.TEXT)
        pygame.draw.rect(surf, T.ACCENT, lst, width=2, border_radius=8)

    def draw(self, surf):
        self.draw_header(surf)
        self.draw_list(surf)