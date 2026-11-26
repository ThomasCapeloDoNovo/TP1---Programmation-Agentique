from .game import Game

class Gomoku(Game):
    """Gomoku.

    état  : tuple de tuple 19*19
    actions : (ligne, colonne)
    """

    def __init__(self, player1=1, player2=2, size=7, align=5):
        super().__init__(player1, player2)
        self.blank = 0
        self.size = size        # nombre d'intersections par côté
        self.align = align      # nombre de pions à aligner
        self.fcteval = EvalGomoku(blank=self.blank, size=size, align=align)
    
    def initial_state(self):
        return tuple(tuple(self.blank for _ in range(self.size)) for _ in range(self.size))

    def player_to_move(self, state):
        """Détermine quel joueur doit jouer en comptant les jetons posés."""
        p1_count = sum(row.count(self.player1) for row in state)
        p2_count = sum(row.count(self.player2) for row in state)
        return self.player1 if p1_count == p2_count else self.player2

    def actions(self, state):
        """Une action est valide si la case est vide."""
        return [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if state[r][c] == self.blank
        ]

    def is_legal(self, state, action):
        ligne, col = action
        return 0 <= ligne < self.size and 0 <= col < self.size and state[ligne][col] == self.blank

    def result(self, state, action):
        if not self.is_legal(state, action) or self.is_terminal(state):
            raise ValueError("Illegal move")
        
        ligne, col = action
        player = self.player_to_move(state)
        board = [list(row) for row in state]
        board[ligne][col] = player
        return tuple(tuple(row) for row in board)

    def winner(self, state):
        """Retourne le joueur gagnant (player1 ou player2), ou None s'il n'y a pas de gagnant."""

        # Alignement horizontale
        for i in range(self.size):
            for j in range(self.size - self.align + 1):
                p = state[i][j]
                if p != self.blank and all(p == state[i][j + k] for k in range(1, self.align)):
                        return p

        # Alignement verticale
        for i in range(self.size - self.align + 1):
            for j in range(self.size):
                p = state[i][j]
                if p != self.blank and all(p == state[i + k][j] for k in range(1, self.align)):
                        return p

        # Algnement diagonale descandant \
        for i in range(self.size - self.align + 1):
            for j in range(self.size - self.align + 1):
                p = state[i][j]
                if p != self.blank and all(p == state[i + k][j + k] for k in range(1, self.align)):
                        return p

        #Alignement diagonale montant /
        for i in range(self.align - 1, self.size):
            for j in range(self.size - self.align + 1):
                p = state[i][j]
                if p != self.blank and all(p == state[i - k ][j + k] for k in range(1, self.align)):
                        return p

        return None

    def is_terminal(self, state):
        """Retourne True si un joueur a gagné ou si la grille est pleine."""
        if self.winner(state) is not None:
            return True
        return all(self.blank not in ligne for ligne in state)

    def evaluate(self, state, player):
        """Evaluation"""
        return self.fcteval.get_eval(state, player)

    def display(self, state):
        """Affichage console."""
        symbols = {self.blank: '.', self.player1: 'X', self.player2: 'O'}
        for ligne in state:
            print(" ".join(symbols.get(cell, str(cell)) for cell in ligne))
        print()


class EvalGomoku:
    """Moteur d'évaluation heuristique pour Gomoku.
    Structure 1:1 avec EvalConnectFour (fenêtres d'alignement + poids positionnels).
    """

    def __init__(self, poids=None, poids_pos=None, blank=0, size = 7, align = 5):
        self.blank = blank
        self.poids = {n: 10 ** n for n in range(1, align)}
        self.poids[align] = 10**9
        
        self._fenetres = self._build_fenetres(size, align)

    def _build_fenetres(self, size, align):
        """Liste des fenêtres de `align` intersections consécutives, calculée une seule fois."""
        fenetres = []
        for l in range(size):
            for c in range(size):
                # horizontale, verticale, diagonale \, diagonale /
                for dl, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    l_fin, c_fin = l + (align - 1) * dl, c + (align - 1) * dc
                    # la fenêtre n'est gardée que si son dernier point est sur le plateau
                    if 0 <= l_fin < size and 0 <= c_fin < size:
                        fenetres.append(tuple((l + i * dl, c + i * dc) for i in range(align)))
        return fenetres

    def get_eval(self, grille, player):
        score = 0

        # Évaluation des fenêtres d'alignement (lignes, colonnes, diagonales)
        for fenetre in self._fenetres:
            moi = 0
            adv = 0
            for r, c in fenetre:
                v = grille[r][c]
                if v == self.blank:
                    continue
                if v == player:
                    moi += 1
                else:
                    adv += 1

            # Fenêtre bloquée si les deux joueurs ont posé au moins un pion
            if moi > 0 and adv > 0:
                continue

            if moi > 0:
                score += self.poids[moi]
            elif adv > 0:
                score -= 1.01 * self.poids[adv]

        return score