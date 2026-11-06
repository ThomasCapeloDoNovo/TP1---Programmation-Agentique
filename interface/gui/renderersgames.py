import pygame
from games.tictactoe import TicTacToe
from games.connectfour import ConnectFour
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

# Registre des renderers de jeux
GAME_RENDERERS = [
    (TicTacToe, TicTacToeRenderer()),
    (ConnectFour, ConnectFourRenderer()),
]

def get_game_renderer(Game: Game):
    for cls, renderer in GAME_RENDERERS:
        if isinstance(Game, cls):
            return renderer
    return GenericGameRenderer()