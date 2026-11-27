import pygame
from games.tictactoe import TicTacToe
from games.connectfour import ConnectFour
from games.isolation import Isolation
from games.quoridor import Quoridor, MOVE, HWALL, VWALL
from games.game import Game
from . import theme as T


class GameRenderer:
    def draw(self, surf, rect, game, state):
        raise NotImplementedError

class GenericGameRenderer(GameRenderer):
    """Secours : affiche simplement le plateau en texte. !! risque de ne pas fonctionner avec les mouvements humains"""

    def draw(self, surf, rect, game, state):
        pygame.draw.rect(surf, T.PANEL, rect, border_radius=10)

        T.draw_text(
            surf,
            str(state),
            (rect.x + 20, rect.y + 20),
            20,
            T.TEXT
        )

    def get_action_from_click(self, pos, rect, game, state):
        return None
    
class TicTacToeRenderer(GameRenderer):
    def draw(self, surf, rect, game, state):
        n = 3
        cell = int(min(rect.w / n, rect.h / n))
        ox = rect.x + (rect.w - cell * n) // 2
        oy = rect.y + (rect.h - cell * n) // 2

        pygame.draw.rect(surf, (40, 44, 52), (ox, oy, cell * n, cell * n), border_radius=8)

        for r in range(n):
            for c in range(n):
                cr = pygame.Rect(ox + c * cell, oy + r * cell, cell, cell)
                pygame.draw.rect(surf, T.PANEL_LIGHT, cr.inflate(-6, -6), border_radius=8)
                
                cell_val = state[r][c]
                if cell_val == game.player1:
                    T.draw_text(surf, "X", cr.center, int(cell * 0.6), T.ACCENT, bold=True, center=True)
                elif cell_val == game.player2:
                    T.draw_text(surf, "O", cr.center, int(cell * 0.6), T.GOOD, bold=True, center=True)

    def get_action_from_click(self, pos, rect, game, state):
        n = 3
        cell = int(min(rect.w / n, rect.h / n))
        ox = rect.x + (rect.w - cell * n) // 2
        oy = rect.y + (rect.h - cell * n) // 2

        # Vérifier si le clic est bien à l'intérieur de la grille de jeu
        if not (ox <= pos[0] < ox + cell * n and oy <= pos[1] < oy + cell * n):
            return None

        col = (pos[0] - ox) // cell
        row = (pos[1] - oy) // cell
        if 0 <= row < n and 0 <= col < n:
            return (row, col)
        return None

class ConnectFourRenderer(GameRenderer):
    def draw(self, surf, rect, game, state):
        rows, cols = game.rows, game.cols
        cell = int(min(rect.w / cols, rect.h / rows))
        ox = rect.x + (rect.w - cell * cols) // 2
        oy = rect.y + (rect.h - cell * rows) // 2

        # Fond du plateau (bleu style Puissance 4)
        board_rect = pygame.Rect(ox, oy, cell * cols, cell * rows)
        pygame.draw.rect(surf, (28, 78, 168), board_rect, border_radius=10)

        for r in range(rows):
            for c in range(cols):
                center = (ox + c * cell + cell // 2, oy + r * cell + cell // 2)
                radius = cell // 2 - 6
                
                cell_val = state[r][c]
                if cell_val == game.blank:
                    color = T.BG  # Trou vide
                elif cell_val == game.player1:
                    color = (235, 87, 87)  # Jeton Rouge (Player 1)
                else:
                    color = (242, 201, 76)  # Jeton Jaune (Player 2)
                
                pygame.draw.circle(surf, color, center, radius)
    
    def get_action_from_click(self, pos, rect, game, state):
        rows, cols = game.rows, game.cols
        cell = int(min(rect.w / cols, rect.h / rows))
        ox = rect.x + (rect.w - cell * cols) // 2
        oy = rect.y + (rect.h - cell * rows) // 2

        # Vérifier si le clic est bien à l'intérieur de la grille de jeu
        if not (ox <= pos[0] < ox + cell * cols and oy <= pos[1] < oy + cell * rows):
            return None

        col = (pos[0] - ox) // cell
        if 0 <= col < cols:
            return col
        return None

class IsolationRenderer(GameRenderer):
    def _geometry(self, rect, game):
        n = game.size
        cell = int(min(rect.w / n, rect.h / n))
        ox = rect.x + (rect.w - cell * n) // 2
        oy = rect.y + (rect.h - cell * n) // 2
        return n, cell, ox, oy

    def draw(self, surf, rect, game, state):
        n, cell, ox, oy = self._geometry(rect, game)

        pygame.draw.rect(surf, (40, 44, 52), (ox, oy, cell * n, cell * n), border_radius=8)

        # Destinations possibles pour le joueur courant (aide visuelle)
        legal_dests = set()
        if not game.is_terminal(state):
            legal_dests = {dest for dest, _ in game.actions(state)}

        for r in range(n):
            for c in range(n):
                cr = pygame.Rect(ox + c * cell, oy + r * cell, cell, cell)
                center = cr.center
                cell_val = state[r][c]

                if cell_val == game.blocked:
                    # Case retirée : plus sombre que le fond du plateau
                    pygame.draw.rect(surf, T.BG, cr.inflate(-6, -6), border_radius=8)
                    continue

                pygame.draw.rect(surf, T.PANEL_LIGHT, cr.inflate(-6, -6), border_radius=8)

                if cell_val == game.player1:
                    pygame.draw.circle(surf, T.ACCENT, center, cell // 2 - 10)
                    T.draw_text(surf, "X", center, int(cell * 0.4), T.BG, bold=True, center=True)
                elif cell_val == game.player2:
                    pygame.draw.circle(surf, T.GOOD, center, cell // 2 - 10)
                    T.draw_text(surf, "O", center, int(cell * 0.4), T.BG, bold=True, center=True)
                elif (r, c) in legal_dests:
                    pygame.draw.circle(surf, T.TEXT, center, max(3, cell // 10))

    def get_action_from_click(self, pos, rect, game, state):
        n, cell, ox, oy = self._geometry(rect, game)

        # Vérifier si le clic est bien à l'intérieur de la grille de jeu
        if not (ox <= pos[0] < ox + cell * n and oy <= pos[1] < oy + cell * n):
            return None

        col = (pos[0] - ox) // cell
        row = (pos[1] - oy) // cell

        # La case retirée est toujours la case de départ du joueur courant
        player = game.player_to_move(state)
        start = game._find_player(state, player)
        if start is None:
            return None

        action = ((row, col), start)
        return action if game.is_legal(state, action) else None
    

class QuoridorRenderer(GameRenderer):
    """Plateau 9x9 avec des gouttières entre les cases pour poser les murs.

    Interaction humaine (un clic = une action) :
      - clic sur une case        -> déplacer le pion (destinations légales marquées d'un point)
      - clic sur une gouttière   -> poser un mur (le mur de 2 cases est centré sur
                                    l'intersection la plus proche du clic ; un aperçu suit la souris)
    """

    max_root_lines = 5

    def _geometry(self, rect, game):
        n = game.size
        side = min(rect.w, rect.h) - 12          # marge pour les barres "ligne but"
        gap = max(8, side // 40)                 # épaisseur d'un mur
        cell = (side - gap * (n - 1)) // n
        pitch = cell + gap
        total = cell * n + gap * (n - 1)
        ox = rect.x + (rect.w - total) // 2
        oy = rect.y + (rect.h - total) // 2
        return n, cell, gap, pitch, total, ox, oy


    def draw(self, surf, rect, game, state):
        n, cell, gap, pitch, total, ox, oy = self._geometry(rect, game)

        # Fond du plateau + lignes but (haut : joueur 2, bas : joueur 1)
        pygame.draw.rect(surf, (40, 44, 52), (ox - 6, oy - 6, total + 12, total + 12), border_radius=8)
        pygame.draw.rect(surf, T.GOOD, (ox, oy - 6, total, 4), border_radius=2)
        pygame.draw.rect(surf, T.ACCENT, (ox, oy + total + 2, total, 4), border_radius=2)

        over = game.is_terminal(state)
        current = None if over else game.player_to_move(state)
        legal = [] if over else game.actions(state)
        legal_dests = {(r, c) for kind, r, c in legal if kind == MOVE}

        for r in range(n):
            for c in range(n):
                cr = pygame.Rect(ox + c * pitch, oy + r * pitch, cell, cell)
                pygame.draw.rect(surf, T.PANEL_LIGHT, cr, border_radius=6)
                if (r, c) in legal_dests:
                    pygame.draw.circle(surf, T.TEXT, cr.center, max(3, cell // 10))

        # Pions
        for player, color, symbol in ((game.player1, T.ACCENT, "X"), (game.player2, T.GOOD, "O")):
            r, c = game.pawn_position(state, player)
            center = (ox + c * pitch + cell // 2, oy + r * pitch + cell // 2)
            radius = cell // 2 - 6
            pygame.draw.circle(surf, color, center, radius)
            T.draw_text(surf, symbol, center, int(cell * 0.45), T.BG, bold=True, center=True)
            if player == current:
                pygame.draw.circle(surf, T.TEXT, center, radius + 3, 2)

        # Murs posés
        for r, c in state.hwalls:
            pygame.draw.rect(surf, T.WARN, self._wall_rect(HWALL, r, c, cell, gap, pitch, ox, oy), border_radius=4)
        for r, c in state.vwalls:
            pygame.draw.rect(surf, T.WARN, self._wall_rect(VWALL, r, c, cell, gap, pitch, ox, oy), border_radius=4)

        # Aperçu sous la souris (seulement si le coup est légal)
        if not over:
            action = self.get_action_from_click(pygame.mouse.get_pos(), rect, game, state)
            if action is not None:
                kind, r, c = action
                if kind == MOVE:
                    cr = pygame.Rect(ox + c * pitch, oy + r * pitch, cell, cell)
                    pygame.draw.rect(surf, T.TEXT, cr, 3, border_radius=6)
                else:
                    wr = self._wall_rect(kind, r, c, cell, gap, pitch, ox, oy)
                    ghost = pygame.Surface(wr.size, pygame.SRCALPHA)
                    pygame.draw.rect(ghost, (*T.WARN, 130), ghost.get_rect(), border_radius=4)
                    surf.blit(ghost, wr.topleft)

    def _wall_rect(self, kind, r, c, cell, gap, pitch, ox, oy):
        """Rectangle d'un mur d'ancre (r, c) : il couvre 2 cases + la gouttière entre elles."""
        if kind == HWALL:
            return pygame.Rect(ox + c * pitch, oy + r * pitch + cell, 2 * cell + gap, gap)
        return pygame.Rect(ox + c * pitch + cell, oy + r * pitch, gap, 2 * cell + gap)

    def side_info(self, surf, x, y, w, game, state):
        """Dessine le nombre de murs restants de chaque joueur. Retourne le nouveau y."""
        current = None if game.is_terminal(state) else game.player_to_move(state)
        T.draw_text(surf, "Murs restants", (x, y), 22, T.TEXT, bold=True)
        y += 30
        for player, color, symbol in ((game.player1, T.ACCENT, "X"), (game.player2, T.GOOD, "O")):
            left = game.walls_left(state, player)
            T.draw_text(surf, f"J{player} ({symbol}) : {left}", (x, y), 20, color, bold=(player == current))
            # une pastille par mur : pleine = encore disponible, vide = déjà posé
            for i in range(game.walls):
                bar = pygame.Rect(x + 120 + i * 17, y + 1, 12, 16)
                if i < left:
                    pygame.draw.rect(surf, T.WARN, bar, border_radius=3)
                else:
                    pygame.draw.rect(surf, T.PANEL_LIGHT, bar, 2, border_radius=3)
            y += 26
        return y + 12

    def _candidates(self, pos, rect, game):
        """Actions possibles sous la souris (la plus probable en premier), sans test de légalité."""
        n, cell, gap, pitch, total, ox, oy = self._geometry(rect, game)
        x, y = pos[0] - ox, pos[1] - oy
        if not (0 <= x < total and 0 <= y < total):
            return []
        margin = min(5, cell // 8)     # tolérance : la gouttière déborde un peu sur les cases

        def zone(v):
            for k in range(n):
                if v < k * pitch + cell - margin:
                    return "cell", k
                if k < n - 1 and v < (k + 1) * pitch + margin:
                    return "gap", k
            return "cell", n - 1

        (zy, r), (zx, c) = zone(y), zone(x)
        last = n - 2                   # dernière ancre possible pour un mur

        def clamp(v):
            return max(0, min(last, v))

        if zx == "cell" and zy == "cell":
            return [(MOVE, r, c)]
        if zy == "gap" and zx == "cell":
            # gouttière horizontale entre les lignes r et r+1, au niveau de la colonne c
            near = c if (x - c * pitch) >= cell / 2 else c - 1
            other = c - 1 if near == c else c
            return [(HWALL, r, clamp(near)), (HWALL, r, clamp(other))]
        if zx == "gap" and zy == "cell":
            # gouttière verticale entre les colonnes c et c+1, au niveau de la ligne r
            near = r if (y - r * pitch) >= cell / 2 else r - 1
            other = r - 1 if near == r else r
            return [(VWALL, clamp(near), c), (VWALL, clamp(other), c)]
        return []                      # intersection : ambigu (mur H ou V), on ignore

    def get_action_from_click(self, pos, rect, game, state):
        if game.is_terminal(state):
            return None
        legal = game.actions(state)
        for action in self._candidates(pos, rect, game):
            if action in legal:
                return action
        return None
    

# Registre des renderers de jeux
GAME_RENDERERS = [
    (TicTacToe, TicTacToeRenderer()),
    (ConnectFour, ConnectFourRenderer()),
    (Isolation, IsolationRenderer()),
    (Quoridor, QuoridorRenderer()),
]

def get_game_renderer(Game: Game):
    for cls, renderer in GAME_RENDERERS:
        if isinstance(Game, cls):
            return renderer
    return GenericGameRenderer()