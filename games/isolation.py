from .game import Game

DIRECTIONS = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
)

def _queen_moves(board, pos, size, blank):
    """Cases atteignables depuis pos en se déplaçant comme une reine."""
    moves = []
    r0, c0 = pos
    for dr, dc in DIRECTIONS:
        r, c = r0 + dr, c0 + dc
        while 0 <= r < size and 0 <= c < size and board[r][c] == blank:
            moves.append((r, c))
            r += dr
            c += dc
    return moves


class Isolation(Game):
    """Isolation (plateau 7x7)
    
    état : tuple de tuple 7*7 (blank, player1, player2 ou blocked)
    actions ((ligne, colonne) d'arrivée, (ligne, colonne) de départ -> de la case retirée)

    règle : - un tour = déplacement du pion (mouvement de reine)
            - la case quittée devient bloquée
            - le joueur qui ne peut plus bouger perd
    
    """

    def __init__(self, player1 = 1, player2 = 2, size = 7):
        super().__init__(player1, player2)
        self.size = size
        self.blank = 0
        self.blocked = -1
        self.fcteval = EvalIsolation(size=self.size, blank = self.blank, blocked=self.blocked)

    # utilitaires
    def _find_player(self, state, player):
        """Retourne la position (ligne, colonne) du pion du joueur."""
        for r in range(self.size):
            for c in range(self.size):
                if state[r][c] == player:
                    return (r, c)
        return None

    # interface game

    def initial_state(self):
        """plateau 7*7, joueur au mileu en haut et en bas"""
        board = [[self.blank for _ in range(self.size)] for _ in range(self.size)]
        mid = self.size // 2
        board[0][mid] = self.player1
        board[self.size - 1][mid] = self.player2
        return tuple(tuple(row) for row in board)

    def player_to_move(self, state):
        """Chaque tour retire exactement une case : la parité des cases bloquées donne le joueur à jouer (player1 commence)"""
        nb_blocked = sum(row.count(self.blocked) for row in state)
        return self.player1 if nb_blocked % 2 == 0 else self.player2

    def actions(self, state):
        """Une action est valide si la case est atteignable et non blocked par le joueur courant"""
        player = self.player_to_move(state)
        pos = self._find_player(state, player)
        if pos is None:
            return []

        actions = []
        for dest in _queen_moves(state, pos, self.size, self.blank):
            actions.append((dest, pos))

        return actions

    def is_legal(self, state, action):
        try:
            (dr, dc), (rr, rc) = action
        except (TypeError, ValueError):
            return False

        n = self.size
        if not (0 <= dr < n and 0 <= dc < n and 0 <= rr < n and 0 <= rc < n):
            return False

        player = self.player_to_move(state)
        pos = self._find_player(state, player)
        if pos is None or (dr, dc) not in _queen_moves(state, pos, n, self.blank):
            return False

        return (rr, rc) == pos

    def result(self, state, action):
        if not self.is_legal(state, action) or self.is_terminal(state):
            raise ValueError("Illegal move")

        (dr, dc), (rr, rc) = action
        player = self.player_to_move(state)

        board = [list(row) for row in state]

        # déplacement du joueur
        board[dr][dc] = player

        # suppression de l'ancienne case
        board[rr][rc] = self.blocked

        return tuple(tuple(row) for row in board)


    def winner(self, state):
        """Le joueur qui doit jouer sans pouvoir bouger perd."""
        to_move = self.player_to_move(state)
        pos = self._find_player(state, to_move)
        if not _queen_moves(state, pos, self.size, self.blank):
            return self.player2 if to_move == self.player1 else self.player1
        return None

    def is_terminal(self, state):
        return self.winner(state) is not None 

    def evaluate(self, state, player):
        return self.fcteval.get_eval(state, player)

    def display(self, state):
        symbols = {
            self.blank: '.',
            self.blocked: '#',
            self.player1: 'X',
            self.player2: 'O',
        }
        print("  " + " ".join(str(c) for c in range(self.size)))
        for i, ligne in enumerate(state):
            print(f"{i} " + " ".join(symbols.get(cell, str(cell)) for cell in ligne))
        print()

class EvalIsolation:
    """Évaluation heuristique pour Isolation :
    un score de mobilité (poids) + un score positionnel (poids_pos).
    """

    def __init__(self, size=7, poids=None, poids_pos=None, blank=0, blocked=-1):
        self.size = size
        self.blank = blank
        self.blocked = blocked
        self.poids = poids if poids is not None else {
            "mobilite": 10,        # nb de coups du joueur
            "mobilite_adv": 10,    # nb de coups de l'adversaire (pénalisé plus fort)
            "position": 1,         # bonus de centralité
            "victoire": 1_000_000,
        }
        # Poids positionnel : plus on est proche du centre, mieux c'est
        mid = (size - 1) / 2
        self.poids_pos = poids_pos if poids_pos is not None else tuple(
            tuple(int(mid - max(abs(r - mid), abs(c - mid))) for c in range(size))
            for r in range(size)
        )

    def _find(self, grille, joueur):
        for r in range(self.size):
            for c in range(self.size):
                if grille[r][c] == joueur:
                    return (r, c)
        return None

    def get_eval(self, grille, player):
        # Identification de l'adversaire (les deux pions présents sur la grille)
        pions = {
            grille[r][c]
            for r in range(self.size)
            for c in range(self.size)
            if grille[r][c] not in (self.blank, self.blocked)
        }
        adversaires = pions - {player}
        if player not in pions or not adversaires:
            return 0
        adv = next(iter(adversaires))

        pos_moi = self._find(grille, player)
        pos_adv = self._find(grille, adv)

        moves_moi = len(_queen_moves(grille, pos_moi, self.size, self.blank))
        moves_adv = len(_queen_moves(grille, pos_adv, self.size, self.blank))

        # Cas terminaux (valable si c'est à l'un des deux de jouer et qu'il est bloqué)
        if moves_moi == 0:
            return -self.poids["victoire"]
        if moves_adv == 0:
            return self.poids["victoire"]

        score = 0
        # 1. Mobilité
        score += self.poids["mobilite"] * moves_moi
        score -= self.poids["mobilite_adv"] * moves_adv

        # 2. Évaluation positionnelle
        score += self.poids["position"] * self.poids_pos[pos_moi[0]][pos_moi[1]]
        score -= 1.01 * self.poids["position"] * self.poids_pos[pos_adv[0]][pos_adv[1]]

        return score