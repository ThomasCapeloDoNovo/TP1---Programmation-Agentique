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
    def __init__(
        self,
        title,
        x,
        y,
        width,
        default_value=0,
        min_value=0,
        max_value=None,
        allow_float=False
    ):
        self.title = title
        self.rect = pygame.Rect(x, y + 28, width, 38)

        self.default_value = str(default_value)
        self.value = self.default_value

        self.min_value = min_value
        self.max_value = max_value
        self.allow_float = allow_float

        self.active = False

    def handle(self, ev):

        if ev.type == pygame.MOUSEBUTTONDOWN:
            was_active = self.active
            self.active = self.rect.collidepoint(ev.pos)

            # Validation quand on quitte le champ
            if was_active and not self.active:
                self.validate()

        elif self.active and ev.type == pygame.KEYDOWN:

            if ev.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]

            elif ev.key == pygame.K_RETURN:
                self.validate()
                self.active = False

            elif ev.unicode.isdigit():
                self.value += ev.unicode

            elif (
                self.allow_float
                and ev.unicode == "."
                and "." not in self.value
            ):
                self.value += "."

    def validate(self):

        if self.value.strip() == "":
            self.value = self.default_value
            return

        try:
            num = float(self.value) if self.allow_float else int(self.value)

            if self.min_value is not None:
                num = max(num, self.min_value)

            if self.max_value is not None:
                num = min(num, self.max_value)

            if self.allow_float:
                self.value = str(num)
            else:
                self.value = str(int(num))

        except ValueError:
            self.value = self.default_value

    @property
    def int_value(self):
        self.validate()
        return int(float(self.value))

    @property
    def float_value(self):
        self.validate()
        return float(self.value)

    def draw(self, surf):

        T.draw_text(
            surf,
            self.title,
            (self.rect.x, self.rect.y - 28),
            22,
            T.MUTED
        )

        pygame.draw.rect(
            surf,
            T.PANEL_LIGHT if self.active else T.PANEL,
            self.rect,
            border_radius=8
        )

        pygame.draw.rect(
            surf,
            T.ACCENT if self.active else T.PANEL_LIGHT,
            self.rect,
            width=2,
            border_radius=8
        )

        T.draw_text(
            surf,
            self.value,
            (self.rect.x + 10, self.rect.centery),
            22,
            T.TEXT
        )