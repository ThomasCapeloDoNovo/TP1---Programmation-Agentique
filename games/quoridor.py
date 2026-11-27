from collections import deque
from typing import NamedTuple
from .game import Game


MOVE = "M"      # déplacement du pion
HWALL = "H"     # mur horizontal
VWALL = "V"     # mur vertical


class QuoridorState(NamedTuple):
    """État immuable et hashable d'une partie de Quoridor.

    pawns      : ((ligne, col) du joueur 1, (ligne, col) du joueur 2)
    walls_left : (murs restants du joueur 1, murs restants du joueur 2)
    hwalls     : frozenset des ancres (ligne, col) des murs horizontaux posés
    vwalls     : frozenset des ancres (ligne, col) des murs verticaux posés
    plies      : nombre de demi-coups déjà joués (donne le joueur courant)
    """
    pawns: tuple
    walls_left: tuple
    hwalls: frozenset
    vwalls: frozenset
    plies: int


def _neighbors(cell, size, hwalls, vwalls):
    """Cases voisines accessibles (4 directions) en tenant compte des murs seulement
    Les pions sont ignorés : c'est la règle pour vérifier qu'un chemin existe
    """

    r, c = cell
    out = []
    if r + 1 < size and (r, c) not in hwalls and (r, c - 1) not in hwalls:
        out.append((r + 1, c))
    if r > 0 and (r - 1, c) not in hwalls and (r - 1, c - 1) not in hwalls:
        out.append((r - 1, c))
    if c + 1 < size and (r, c) not in vwalls and (r - 1, c) not in vwalls:
        out.append((r, c + 1))
    if c > 0 and (r, c - 1) not in vwalls and (r - 1, c - 1) not in vwalls:
        out.append((r, c - 1))
    return out


def _shortest_path(start, goal_row, size, hwalls, vwalls):
    """Plus court chemin (liste de cases, départ inclus) vers la ligne but, ou None"""
    prev = {start: None}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        if cur[0] == goal_row:
            path = []
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            path.reverse()
            return path
        for nxt in _neighbors(cur, size, hwalls, vwalls):
            if nxt not in prev:
                prev[nxt] = cur
                queue.append(nxt)
    return None


class Quoridor(Game):
    """Quoridor (plateau 9x9, 10 murs par joueur)

    état : QuoridorState cf au dessus
    actions : tuples (type, ligne, colonne), indices 0-based
        ('M', r, c) : déplacer le pion en (r, c)
        ('H', r, c) : mur horizontal sous les cases (r, c) et (r, c+1)
        ('V', r, c) : mur vertical à droite des cases (r, c) et (r+1, c)
        pour les murs, 0 <= r, c <= size-2 (ancre = coin haut-gauche du mur de 2 cases)

    règle : - un tour = déplacer son pion ou poser un mur (si il en reste)
            - le pion avance d'une case orthogonale, saute l'adversaire adjacent,
              ou passe en diagonale si un mur / le bord bloque le saut
            - un mur ne peut ni en croiser/chevaucher un autre, ni enfermer
              complètement un joueur (un chemin vers son but doit toujours exister)
            - joueur 1 part en haut et vise la dernière ligne, joueur 2 l'inverse
            - le premier arrivé sur sa ligne but gagne
            - au bout de max_turns demi-coups la partie est déclarée nulle
              (garantit que les simulations aléatoires de MCTS se terminent)
    """

    def __init__(self, player1=1, player2=2, size=9, walls=10, max_turns=200):
        super().__init__(player1, player2)
        self.size = size
        self.walls = walls
        self.max_turns = max_turns
        self.fcteval = EvalQuoridor(size=size, player1=player1, player2=player2)
        n = size
        self._move_action = {(r, c): (MOVE, r, c) for r in range(n) for c in range(n)}
        self._wall_actions = [
            (kind, r, c)
            for kind in (HWALL, VWALL)
            for r in range(n - 1)
            for c in range(n - 1)
        ]
        self._wall_edges = {}                                                   # Cases coupées par chaque mur (arêtes entre deux cases voisines, ordre normalisé)
        for kind, r, c in self._wall_actions:
            if kind == HWALL:
                edges = (((r, c), (r + 1, c)), ((r, c + 1), (r + 1, c + 1)))
            else:
                edges = (((r, c), (r, c + 1)), ((r + 1, c), (r + 1, c + 1)))
            self._wall_edges[(kind, r, c)] = edges
        self._walls_near = {                                                    # Ordre de génération des murs : ceux proches de l'adversaire d'abord (aide l'alpha-bêta)
            (pr, pc): sorted(
                self._wall_actions,
                key=lambda a: abs(a[1] + 0.5 - pr) + abs(a[2] + 0.5 - pc),
            )
            for pr in range(n) for pc in range(n)
        }
        self._cache = {}                                                        # Cache des actions légales des derniers états consultés (actions() -> result() -> is_legal())

    # utilitaire 

    def _idx(self, player):
        """Indice (0 ou 1) du joueur dans les tuples de l'état."""
        return 0 if player == self.player1 else 1

    def _goal_row(self, idx):
        return self.size - 1 if idx == 0 else 0

    def walls_left(self, state, player):
        """Nombre de murs que le joueur peut encore poser."""
        return state.walls_left[self._idx(player)]

    def pawn_position(self, state, player):
        """Position (ligne, colonne) du pion du joueur."""
        return state.pawns[self._idx(player)]

    def shortest_distance(self, state, player):
        """Nombre de cases restantes sur le plus court chemin du joueur (pions ignorés)."""
        idx = self._idx(player)
        path = _shortest_path(state.pawns[idx], self._goal_row(idx), self.size, state.hwalls, state.vwalls)
        return len(path) - 1 if path else None

    def _blocked(self, a, b, hwalls, vwalls):
        """True si un mur sépare les deux cases adjacentes a et b."""
        (r, c), (r2, c2) = a, b
        if c == c2:
            low = min(r, r2)
            return (low, c) in hwalls or (low, c - 1) in hwalls
        left = min(c, c2)
        return (r, left) in vwalls or (r - 1, left) in vwalls

    def _pawn_moves(self, state, idx):
        """Destinations légales du pion (sauts et diagonales inclus)."""
        n = self.size
        moi = state.pawns[idx]
        adv = state.pawns[1 - idx]
        h, v = state.hwalls, state.vwalls
        forward = 1 if idx == 0 else -1
        directions = ((forward, 0), (0, -1), (0, 1), (-forward, 0))

        def inside(cell):
            return 0 <= cell[0] < n and 0 <= cell[1] < n

        moves = []
        for dr, dc in directions:
            nxt = (moi[0] + dr, moi[1] + dc)
            if not inside(nxt) or self._blocked(moi, nxt, h, v):
                continue
            if nxt != adv:
                moves.append(nxt)
                continue
            # adversaire adjacent : saut en ligne droite si possible
            jump = (nxt[0] + dr, nxt[1] + dc)
            if inside(jump) and not self._blocked(nxt, jump, h, v):
                moves.append(jump)
                continue
            # sinon, pas de côté (diagonale) autour de l'adversaire
            for pr, pc in ((dc, dr), (-dc, -dr)):
                diag = (nxt[0] + pr, nxt[1] + pc)
                if inside(diag) and not self._blocked(nxt, diag, h, v):
                    moves.append(diag)
        return moves

    def _wall_free(self, state, kind, r, c):
        """True si le mur ne chevauche ni ne croise un mur existant."""
        h, v = state.hwalls, state.vwalls
        if kind == HWALL:
            return (r, c) not in h and (r, c - 1) not in h and (r, c + 1) not in h and (r, c) not in v
        return (r, c) not in v and (r - 1, c) not in v and (r + 1, c) not in v and (r, c) not in h

    def _is_over(self, state):
        return (
            state.pawns[0][0] == self._goal_row(0)
            or state.pawns[1][0] == self._goal_row(1)
            or state.plies >= self.max_turns
        )

    def _compute_actions(self, state):
        if self._is_over(state):
            return []
        idx = state.plies % 2
        n = self.size
        actions = [self._move_action[cell] for cell in self._pawn_moves(state, idx)]

        if state.walls_left[idx] > 0:
            goals = (self._goal_row(0), self._goal_row(1))
            # arêtes du chemin le plus court actuel de chaque joueur : un mur qui n'en coupe
            # aucune ne peut pas enfermer ce joueur (évite la plupart des BFS)
            path_edges = []
            for i in (0, 1):
                path = _shortest_path(state.pawns[i], goals[i], n, state.hwalls, state.vwalls)
                path_edges.append({
                    (a, b) if a < b else (b, a) for a, b in zip(path, path[1:])
                })

            for action in self._walls_near[state.pawns[1 - idx]]:
                kind, r, c = action
                if not self._wall_free(state, kind, r, c):
                    continue
                edges = self._wall_edges[action]
                new_h, new_v = state.hwalls, state.vwalls
                ok = True
                for i in (0, 1):
                    if path_edges[i].isdisjoint(edges):
                        continue
                    if new_h is state.hwalls and new_v is state.vwalls:
                        if kind == HWALL:
                            new_h = state.hwalls | {(r, c)}
                        else:
                            new_v = state.vwalls | {(r, c)}
                    if _shortest_path(state.pawns[i], goals[i], n, new_h, new_v) is None:
                        ok = False
                        break
                if ok:
                    actions.append(action)
        return actions

    # interface game

    def initial_state(self):
        """plateau 9*9, pions au milieu des lignes du haut (joueur 1) et du bas (joueur 2)"""
        mid = self.size // 2
        return QuoridorState(
            pawns=((0, mid), (self.size - 1, mid)),
            walls_left=(self.walls, self.walls),
            hwalls=frozenset(),
            vwalls=frozenset(),
            plies=0,
        )

    def player_to_move(self, state):
        """Un tour = un demi-coup : la parité donne le joueur à jouer (player1 commence)"""
        return self.player1 if state.plies % 2 == 0 else self.player2

    def actions(self, state):
        """Déplacements du pion d'abord, puis les murs légaux (proches de l'adversaire en premier)"""
        cached = self._cache.get(state)
        if cached is None:
            cached = tuple(self._compute_actions(state))
            if len(self._cache) > 2048:
                self._cache.clear()
            self._cache[state] = cached
        return list(cached)

    def is_legal(self, state, action):
        try:
            kind, r, c = action
        except (TypeError, ValueError):
            return False
        if kind not in (MOVE, HWALL, VWALL) or not isinstance(r, int) or not isinstance(c, int):
            return False
        return (kind, r, c) in self.actions(state)

    def result(self, state, action):
        if self.is_terminal(state) or not self.is_legal(state, action):
            raise ValueError("Illegal move")

        kind, r, c = action
        idx = state.plies % 2
        pawns, walls_left = state.pawns, state.walls_left
        hwalls, vwalls = state.hwalls, state.vwalls

        if kind == MOVE:
            pawns = tuple((r, c) if i == idx else p for i, p in enumerate(pawns))
        else:
            walls_left = tuple(w - 1 if i == idx else w for i, w in enumerate(walls_left))
            if kind == HWALL:
                hwalls = hwalls | {(r, c)}
            else:
                vwalls = vwalls | {(r, c)}

        return QuoridorState(pawns, walls_left, hwalls, vwalls, state.plies + 1)

    def winner(self, state):
        """Le premier pion arrivé sur sa ligne but gagne (None si nul ou partie en cours)."""
        if state.pawns[0][0] == self._goal_row(0):
            return self.player1
        if state.pawns[1][0] == self._goal_row(1):
            return self.player2
        return None

    def is_terminal(self, state):
        return self._is_over(state)

    def evaluate(self, state, player):
        return self.fcteval.get_eval(state, player)

    # affichage / textes

    def format_action(self, action):
        """Action -> texte court, coordonnées 1-based (L = ligne, C = colonne)."""
        kind, r, c = action
        if kind == MOVE:
            return f"Pion L{r + 1} C{c + 1}"
        return f"Mur {kind} L{r + 1} C{c + 1}"

    def display(self, state):
        n = self.size
        size = 2 * n - 1
        grid = [[" "] * size for _ in range(size)]
        for r in range(n):
            for c in range(n):
                grid[2 * r][2 * c] = "."
        grid[state.pawns[0][0] * 2][state.pawns[0][1] * 2] = "X"
        grid[state.pawns[1][0] * 2][state.pawns[1][1] * 2] = "O"
        for r, c in state.hwalls:
            for k in range(3):
                grid[2 * r + 1][2 * c + k] = "-"
        for r, c in state.vwalls:
            for k in range(3):
                grid[2 * r + k][2 * c + 1] = "|"

        print("  " + " ".join(str(c + 1) for c in range(n)))
        for i, row in enumerate(grid):
            label = str(i // 2 + 1) if i % 2 == 0 else " "
            print(f"{label} " + "".join(row))
        print(f"Murs restants : X = {state.walls_left[0]}, O = {state.walls_left[1]}")
        print()


class EvalQuoridor:
    """Évaluation heuristique pour Quoridor :
    différence de plus courts chemins (poids) + différence de murs en réserve (poids_murs).
    """

    def __init__(self, size=9, player1=1, player2=2, poids=None):
        self.size = size
        self.player1 = player1
        self.player2 = player2
        self.poids = poids if poids is not None else {
            "chemin": 10,          # chaque case gagnée sur l'adversaire
            "murs": 3,             # chaque mur de plus en réserve
            "victoire": 1_000_000,
        }

    def get_eval(self, state, player):
        moi = 0 if player == self.player1 else 1
        adv = 1 - moi
        goals = (self.size - 1, 0)

        # Cas terminaux
        if state.pawns[moi][0] == goals[moi]:
            return self.poids["victoire"]
        if state.pawns[adv][0] == goals[adv]:
            return -self.poids["victoire"]

        d_moi = _shortest_path(state.pawns[moi], goals[moi], self.size, state.hwalls, state.vwalls)
        d_adv = _shortest_path(state.pawns[adv], goals[adv], self.size, state.hwalls, state.vwalls)
        if d_moi is None or d_adv is None:
            return 0

        score = 0
        # 1. Mobilité
        score += self.poids["chemin"] * (len(d_adv) - len(d_moi))
        
        # 2. Murs en réserve
        score += self.poids["murs"] * (state.walls_left[moi] - state.walls_left[adv])
        return score