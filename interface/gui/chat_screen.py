# interface/chat_screen.py
import queue
import re
import time
from itertools import groupby

import pygame

from .widgets import Button
from . import theme as T
from agentic.chat_backend import ChatBackend

WELCOME = (
    "Salut ! Je suis AUSSI. Je peux jouer au morpion ou au puissance 4 avec toi.\n"
    "Essaie par exemple : « on joue au morpion »."
)


class ChatScreen:
    CHAT_RECT = pygame.Rect(20, 80, 1060, 540)
    INPUT_RECT = pygame.Rect(20, 635, 830, 50)

    FS = 20          # taille de police des messages
    PAD = 12         # padding intérieur d'une bulle
    GAP = 12         # espace entre deux bulles
    BOX_PAD = 8      # padding intérieur de la boîte de code (plateau)
    MAX_BUBBLE_W = 760

    def __init__(self, app, back=None):
        """
        back : fonction sans argument qui renvoie l'écran vers lequel revenir
               (ex. lambda: GameMenuScreen(app)).
        """
        self.app = app
        self.back = back

        # L'état du chat survit aux changements d'onglet.
        if not hasattr(app, "chat_state"):
            app.chat_state = {"backend": ChatBackend(), "log": [], "busy": False, "status": ""}
        self.st = app.chat_state
        self.backend = self.st["backend"]

        self.font = T.font(self.FS)
        self.font_bold = T.font(16, bold=True)
        self.mono = pygame.font.SysFont("dejavusansmono,couriernew,consolas,menlo,monospace", self.FS - 2)

        self.input_text = ""
        self.scroll_y = 0
        self.max_scroll = 0
        self.stick_bottom = True

        self.menu_btn = Button((1100 - 190, 22, 170, 40), "Menu (Échap)", self.back_to_menu)
        self.send_btn = Button((860, 635, 110, 50), "Envoyer", self.send)
        self.reset_btn = Button((980, 635, 100, 50), "Reset", self.reset)

        if not self.st["log"]:
            self._add("assistant", WELCOME)
        else:
            for m in self.st["log"]:       # re-layout (la police peut avoir changé)
                self._layout(m)

        pygame.key.set_repeat(400, 35)     # backspace maintenu

    # ------------------------------------------------------------------ messages

    def _wrap(self, text, max_w):
        """
        Découpe le texte en lignes (texte, is_mono).
        Les blocs ``` ... ``` sont renvoyés en is_mono=True (sans les ```),
        sans retour à la ligne automatique.
        """
        lines = []
        in_code = False
        block_start = 0

        # "```text" ou "```" collés à du contenu -> fence sur sa propre ligne
        text = re.sub(r"```[a-zA-Z]*", "\n```\n", text)

        for para in text.split("\n"):
            if para.strip() == "```":
                if in_code:
                    # fermeture : on retire les lignes vides de fin de bloc
                    while len(lines) > block_start and lines[-1] == ("", True):
                        lines.pop()
                else:
                    block_start = len(lines)
                in_code = not in_code
                continue

            if in_code:
                if not para.strip() and len(lines) == block_start:
                    continue                      # ligne vide en début de bloc
                lines.append((para.rstrip(), True))
                continue

            para = para.replace("`", "")          # `code inline` -> texte simple
            if not para.strip():
                lines.append(("", False))
                continue

            cur = ""
            for word in para.split(" "):
                test = word if not cur else cur + " " + word
                if self.font.size(test)[0] <= max_w:
                    cur = test
                else:
                    if cur:
                        lines.append((cur, False))
                    cur = word
            lines.append((cur, False))
        return lines

    def _layout(self, m):
        max_text_w = self.MAX_BUBBLE_W - 2 * self.PAD
        lines = self._wrap(m["text"], max_text_w)
        lh = self.font.get_linesize()

        widths = [
            self.mono.size(t)[0] + 2 * self.BOX_PAD if mono else self.font.size(t)[0]
            for t, mono in lines
        ]
        n_boxes = sum(1 for is_mono, _ in groupby(lines, key=lambda l: l[1]) if is_mono)

        m["lines"] = lines
        m["w"] = max(widths + [80]) + 2 * self.PAD
        # 20 = ligne d'étiquette ; chaque boîte ajoute 2 * BOX_PAD de hauteur
        m["h"] = 20 + len(lines) * lh + n_boxes * 2 * self.BOX_PAD + 2 * self.PAD

    def _add(self, role, text):
        m = {"role": role, "text": text}
        self._layout(m)
        self.st["log"].append(m)
        self.stick_bottom = True

    # ------------------------------------------------------------------ actions

    def back_to_menu(self):
        pygame.key.set_repeat()   # désactive la répétition pour les autres écrans
        if self.back:
            self.app.screen_obj = self.back()

    def send(self):
        text = self.input_text.strip()
        if not text or self.st["busy"]:
            return
        self._add("user", text)
        self.input_text = ""
        self.st["busy"] = True
        self.st["status"] = "AUSSI réfléchit"
        self.backend.send(text)

    def reset(self):
        if self.st["busy"]:
            return
        self.backend.reset()
        self.st["log"].clear()
        self._add("assistant", WELCOME)

    # ------------------------------------------------------------------ events

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.menu_btn.click(ev.pos)
            self.send_btn.click(ev.pos)
            self.reset_btn.click(ev.pos)

        elif ev.type == pygame.MOUSEWHEEL:
            self.scroll_y -= ev.y * 50
            self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
            self.stick_bottom = self.scroll_y >= self.max_scroll

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                self.back_to_menu()
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.send()
            elif ev.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif ev.key == pygame.K_PAGEUP:
                self.scroll_y = max(0, self.scroll_y - 300)
                self.stick_bottom = False
            elif ev.key == pygame.K_PAGEDOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + 300)
                self.stick_bottom = self.scroll_y >= self.max_scroll
            elif ev.unicode and ev.unicode.isprintable() and len(self.input_text) < 500:
                self.input_text += ev.unicode

    def update(self, dt):
        while True:
            try:
                kind, payload = self.backend.events.get_nowait()
            except queue.Empty:
                break
            if kind == "status":
                self.st["status"] = payload
            elif kind == "answer":
                self._add("assistant", payload)
            elif kind == "error":
                self._add("error", payload)
            elif kind == "done":
                self.st["busy"] = False
                self.st["status"] = ""

    # ------------------------------------------------------------------ dessin

    def draw(self, surf):
        surf.fill(T.BG)

        T.draw_text(surf, "Chat avec AUSSI", (20, 30), 32, T.TEXT, bold=True)
        if self.st["busy"]:
            dots = "." * (int(time.time() * 3) % 4)
            T.draw_text(surf, self.st["status"] + dots, (340, 38), 20, T.WARN, bold=True)
        self.menu_btn.draw(surf)

        pygame.draw.rect(surf, T.PANEL, self.CHAT_RECT, border_radius=10)
        self._draw_messages(surf)
        self._draw_input(surf)

    def _draw_messages(self, surf):
        inner = self.CHAT_RECT.inflate(-24, -24)
        lh = self.font.get_linesize()

        content_h = sum(m["h"] + self.GAP for m in self.st["log"])
        self.max_scroll = max(0, content_h - inner.h)
        if self.stick_bottom:
            self.scroll_y = self.max_scroll
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

        old_clip = surf.get_clip()
        surf.set_clip(inner)

        y = inner.y - self.scroll_y
        for m in self.st["log"]:
            if y + m["h"] >= inner.y and y <= inner.bottom:
                role = m["role"]
                if role == "user":
                    x = inner.right - m["w"]
                    bg, border, label, lcolor = T.PANEL_LIGHT, T.PANEL_LIGHT, "Moi", T.MUTED
                elif role == "error":
                    x = inner.x
                    bg, border, label, lcolor = T.BG, T.WARN, "Erreur", T.WARN
                else:
                    x = inner.x
                    bg, border, label, lcolor = T.BG, T.ACCENT, "AUSSI", T.ACCENT

                rect = pygame.Rect(x, y, m["w"], m["h"])
                pygame.draw.rect(surf, bg, rect, border_radius=10)
                pygame.draw.rect(surf, border, rect, width=1, border_radius=10)

                surf.blit(self.font_bold.render(label, True, lcolor), (x + self.PAD, y + 8))

                ty = y + self.PAD + 20
                text_color = T.WARN if role == "error" else T.TEXT

                # On regroupe les lignes consécutives de même type (texte / code)
                for is_mono, group in groupby(m["lines"], key=lambda l: l[1]):
                    group = list(group)

                    if is_mono:
                        bw = max(self.mono.size(t)[0] for t, _ in group) + 2 * self.BOX_PAD
                        bh = len(group) * lh + 2 * self.BOX_PAD
                        box = pygame.Rect(x + self.PAD, ty, bw, bh)
                        pygame.draw.rect(surf, T.PANEL, box, border_radius=8)
                        pygame.draw.rect(surf, T.PANEL_LIGHT, box, width=1, border_radius=8)

                        ty += self.BOX_PAD
                        for t, _ in group:
                            surf.blit(self.mono.render(t, True, T.TEXT), (box.x + self.BOX_PAD, ty))
                            ty += lh
                        ty += self.BOX_PAD
                    else:
                        for t, _ in group:
                            if t:
                                surf.blit(self.font.render(t, True, text_color), (x + self.PAD, ty))
                            ty += lh
            y += m["h"] + self.GAP

        surf.set_clip(old_clip)

        # petite barre de défilement
        if self.max_scroll > 0:
            track = pygame.Rect(self.CHAT_RECT.right - 10, inner.y, 4, inner.h)
            thumb_h = max(30, int(inner.h * inner.h / content_h))
            thumb_y = track.y + int((track.h - thumb_h) * self.scroll_y / self.max_scroll)
            pygame.draw.rect(surf, T.PANEL_LIGHT, pygame.Rect(track.x, thumb_y, 4, thumb_h), border_radius=2)

    def _draw_input(self, surf):
        busy = self.st["busy"]
        pygame.draw.rect(surf, T.PANEL, self.INPUT_RECT, border_radius=10)
        pygame.draw.rect(surf, T.WARN if busy else T.ACCENT, self.INPUT_RECT, width=1, border_radius=10)

        max_w = self.INPUT_RECT.w - 28
        if self.input_text:
            shown = self.input_text
            while shown and self.font.size(shown)[0] > max_w:
                shown = shown[1:]
            img = self.font.render(shown, True, T.TEXT)
        else:
            img = self.font.render("Écris un message… (Entrée pour envoyer)", True, T.MUTED)

        ty = self.INPUT_RECT.centery - img.get_height() // 2
        surf.blit(img, (self.INPUT_RECT.x + 14, ty))

        # curseur clignotant
        if self.input_text and int(time.time() * 2) % 2 == 0:
            cx = self.INPUT_RECT.x + 14 + img.get_width() + 2
            pygame.draw.line(surf, T.TEXT, (cx, ty), (cx, ty + img.get_height()), 2)

        self.send_btn.draw(surf)
        self.reset_btn.draw(surf)