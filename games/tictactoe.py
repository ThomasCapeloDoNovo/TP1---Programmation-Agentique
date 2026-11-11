from .game import Game


class TicTacToe(Game):
    """TicTacToe (Morpion 3x3).

    état  : tuple de tuple 3*3
    actions : (ligne, colonne)
    """

    def __init__(self, player1=1, player2=2):
        super().__init__(player1, player2)
        self.blank = 0
        self.fcteval = EvalTicTacToe(blank=self.blank)
    
    def initial_state(self):
        return tuple(tuple(self.blank for _ in range(3)) for _ in range(3))

    def player_to_move(self, state):
        """Détermine quel joueur doit jouer en comptant les jetons posés."""
        p1_count = sum(row.count(self.player1) for row in state)
        p2_count = sum(row.count(self.player2) for row in state)
        return self.player1 if p1_count == p2_count else self.player2

    def actions(self, state):
        """Une action est valide si la case est vide."""
        return [
            (r, c)
            for r in range(3)
            for c in range(3)
            if state[r][c] == self.blank
        ]

    def is_legal(self, state, action):
        ligne, col = action
        return 0 <= ligne < 3 and 0 <= col < 3 and state[ligne][col] == self.blank

    def result(self, state, action):
        if not self.is_legal(state, action) or self.is_terminal(state)[0]:
            raise ValueError("Illegal move")
        
        ligne, col = action
        player = self.player_to_move(state)
        board = [list(row) for row in state]
        board[ligne][col] = player
        return tuple(tuple(row) for row in board)

    def winner(self, state):
        """Retourne le joueur gagnant (player1 ou player2), ou None s'il n'y a pas de gagnant."""
        lines = []
        # Lignes
        lines.extend(state)
        # Colonnes
        lines.extend(tuple(state[r][c] for r in range(3)) for c in range(3))
        # Diagonales
        lines.append(tuple(state[i][i] for i in range(3)))
        lines.append(tuple(state[i][2 - i] for i in range(3)))

        for line in lines:
            if line[0] != self.blank and all(cell == line[0] for cell in line):
                return line[0]

        return None

    def is_terminal(self, state):
        """True si le jeu est fini (gagnant ou grille pleine)."""
        w = self.winner(state)
        if w is not None:
            return True, w

        if all(self.blank not in ligne for ligne in state):
            return True, None

        return False, None

    def evaluate(self, state, player):
        """Evaluation"""
        return self.fcteval.get_eval(state, player)

    def display(self, state):
        """Affichage console."""
        symbols = {self.blank: '.', self.player1: 'X', self.player2: 'O'}
        for ligne in state:
            print(" ".join(symbols.get(cell, str(cell)) for cell in ligne))
        print()


class EvalTicTacToe:
    """Moteur d'évaluation heuristique pour Tic-Tac-Toe.
    Structure 1:1 avec EvalConnectFour (fenêtres d'alignement + poids positionnels).
    """

    def __init__(self, poids=None, poids_pos=None, blank=0):
        self.blank = blank
        self.poids = poids if poids is not None else {
            1: 10,
            2: 100,
            3: 100000,
        }
        self.poids_pos = poids_pos if poids_pos is not None else (
            (3, 2, 3),
            (2, 4, 2),
            (3, 2, 3)
        )
        
        self._fenetres = self._build_fenetres()

    def _build_fenetres(self):
        """Génère les 8 fenêtres de 3 cases."""
        fenetres = []
        for r in range(3):
            fenetres.append(tuple((r, c) for c in range(3)))
        for c in range(3):
            fenetres.append(tuple((r, c) for r in range(3)))
        fenetres.append(tuple((i, i) for i in range(3)))
        fenetres.append(tuple((i, 2 - i) for i in range(3)))
        return fenetres

    def get_eval(self, grille, player):
        score = 0

        # 1. Évaluation positionnelle
        for r in range(3):
            for c in range(3):
                v = grille[r][c]
                if v == self.blank:
                    continue
                if v == player:
                    score += self.poids_pos[r][c]
                else:
                    score -= 1.01 * self.poids_pos[r][c]

        # 2. Évaluation des fenêtres d'alignement (lignes, colonnes, diagonales)
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