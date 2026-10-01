"""Couleurs et polices communes."""
import pygame

BG = (22, 26, 34)
PANEL = (34, 40, 52)
PANEL_LIGHT = (48, 56, 72)
ACCENT = (86, 156, 214)
ACCENT_DARK = (52, 98, 140)
TEXT = (230, 233, 238)
MUTED = (140, 148, 160)
GOOD = (102, 187, 106)
BAD = (229, 115, 115)
WARN = (255, 183, 77)

_fonts = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        f = pygame.font.Font(None, size)
        f.set_bold(bold)
        _fonts[key] = f
    return _fonts[key]


def draw_text(surf, text, pos, size=24, color=TEXT, bold=False, center=False):
    img = font(size, bold).render(str(text), True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surf.blit(img, rect)
    return rect


def wrap_text(text, size, max_width):
    f, lines, cur = font(size), [], ""
    for word in str(text).split(" "):
        test = (cur + " " + word).strip()
        if f.size(test)[0] <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines
