"""Couleurs, thèmes et polices communes."""
import json
from pathlib import Path

import pygame

# Fichier de sauvegarde (à la racine du projet, adapte si besoin)
SETTINGS_FILE = Path(__file__).resolve().parent.parent.parent / "settings.json"

THEMES = {
    "sombre": {
        "label": "Sombre",
        "colors": dict(
            BG=(22, 26, 34), PANEL=(34, 40, 52), PANEL_LIGHT=(48, 56, 72),
            ACCENT=(86, 156, 214), ACCENT_DARK=(52, 98, 140),
            TEXT=(230, 233, 238), MUTED=(140, 148, 160),
            GOOD=(102, 187, 106), BAD=(229, 115, 115), WARN=(255, 183, 77),
            BOARD=(40, 44, 52),
        ),
    },
    "clair": {
        "label": "Clair",
        "colors": dict(
            BG=(240, 242, 246), PANEL=(225, 229, 236), PANEL_LIGHT=(207, 213, 224),
            ACCENT=(66, 133, 244), ACCENT_DARK=(40, 90, 180),
            TEXT=(30, 34, 42), MUTED=(100, 108, 120),
            GOOD=(46, 150, 80), BAD=(210, 70, 70), WARN=(230, 140, 20),
            BOARD=(190, 197, 210),
        ),
    },
    "printemps": {
        "label": "Printemps",
        "colors": dict(
            BG=(238, 247, 238), PANEL=(214, 236, 214), PANEL_LIGHT=(190, 222, 190),
            ACCENT=(236, 120, 170), ACCENT_DARK=(180, 70, 120),
            TEXT=(40, 60, 40), MUTED=(100, 130, 100),
            GOOD=(60, 160, 80), BAD=(210, 80, 80), WARN=(240, 170, 40),
            BOARD=(170, 205, 170),
        ),
    },
    "ete": {
        "label": "Été",
        "colors": dict(
            BG=(255, 246, 220), PANEL=(255, 232, 175), PANEL_LIGHT=(255, 218, 130),
            ACCENT=(0, 150, 200), ACCENT_DARK=(0, 100, 140),
            TEXT=(60, 45, 20), MUTED=(140, 120, 70),
            GOOD=(40, 160, 100), BAD=(220, 70, 60), WARN=(240, 130, 20),
            BOARD=(240, 200, 110),
        ),
    },
    "automne": {
        "label": "Automne",
        "colors": dict(
            BG=(40, 28, 20), PANEL=(62, 42, 30), PANEL_LIGHT=(88, 60, 42),
            ACCENT=(222, 130, 40), ACCENT_DARK=(160, 85, 20),
            TEXT=(245, 230, 210), MUTED=(170, 145, 120),
            GOOD=(150, 180, 70), BAD=(210, 80, 60), WARN=(240, 190, 60),
            BOARD=(55, 38, 28),
        ),
    },
    "hiver": {
        "label": "Hiver",
        "colors": dict(
            BG=(228, 238, 248), PANEL=(206, 222, 240), PANEL_LIGHT=(184, 206, 230),
            ACCENT=(70, 130, 200), ACCENT_DARK=(40, 85, 140),
            TEXT=(25, 40, 60), MUTED=(95, 115, 140),
            GOOD=(50, 150, 130), BAD=(200, 80, 90), WARN=(230, 150, 50),
            BOARD=(170, 195, 222),
        ),
    },
    "noel": {
        "label": "Noël",
        "colors": dict(
            BG=(14, 36, 24), PANEL=(24, 56, 38), PANEL_LIGHT=(40, 82, 56),
            ACCENT=(204, 40, 48), ACCENT_DARK=(140, 24, 30),
            TEXT=(248, 244, 232), MUTED=(160, 185, 165),
            GOOD=(255, 215, 90), BAD=(255, 110, 110), WARN=(255, 190, 80),
            BOARD=(20, 48, 32),
        ),
    },
}
DEFAULT_THEME = "sombre"
current_theme = DEFAULT_THEME

# Valeurs initiales (remplacées par set_theme juste en dessous)
BG = PANEL = PANEL_LIGHT = ACCENT = ACCENT_DARK = (0, 0, 0)
TEXT = MUTED = GOOD = BAD = WARN = BOARD = (0, 0, 0)


# ---------- Persistance ----------
def load_settings():
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_settings(**changes):
    data = load_settings()
    data.update(changes)
    try:
        SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass  # pas grave si on ne peut pas écrire


def set_theme(key, save=True):
    """Change les couleurs globales. Tous les T.XXX lus ensuite sont à jour."""
    global current_theme
    if key not in THEMES:
        key = DEFAULT_THEME
    globals().update(THEMES[key]["colors"])
    current_theme = key
    if save:
        save_settings(theme=key)


# Au chargement du module : on applique le thème sauvegardé
set_theme(load_settings().get("theme", DEFAULT_THEME), save=False)


# ---------- Polices / texte ----------
_fonts = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        f = pygame.font.Font(None, size)
        f.set_bold(bold)
        _fonts[key] = f
    return _fonts[key]


def draw_text(surf, text, pos, size=24, color=None, bold=False, center=False):
    if color is None:          # lu à l'appel, donc suit le thème
        color = TEXT
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