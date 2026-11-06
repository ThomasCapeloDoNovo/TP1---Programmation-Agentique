from .game import Game

class ConnectFour(Game):
    """Puissance 4.

    état  : tuple de tuple 6 lignes * 7 colonnes, (0, 0) en haut à gauche de la grille
    actions : index de la colonne (int de 0 à 6)
    """

    def __init__(self, player1 = 1, player2 = 2, rows = 6, cols = 7):
        super().__init__(player1, player2)
        self.blank = 0
        self.rows = rows
        self.cols = cols
    
    def initial_state(self):
        return tuple(tuple(self.blank for _ in range(self.cols)) for _ in range(self.rows))

    def player_to_move(self, state):
        """Détermine quel joueur doit jouer en comptant les jetons posés. player1 commence toujours"""
        p1_count = 0
        p2_count = 0

        for ligne in state:
            for col in ligne:
                if col == self.player1:
                    p1_count += 1
                elif col == self.player2:
                    p2_count += 1

        if p1_count == p2_count:
            return self.player1
        return self.player2

    def actions(self, state):
        """Une action est valide si la case tout en haut de la colonne est vide."""
        actions = []
        for col in range(self.cols):
            if state[0][col] == self.blank:
                actions.append(col)
        return actions

    def is_legal(self, state, action):
        if not isinstance(action, int) or action < 0 or action >= self.cols:
            return False
        return state[0][action] == self.blank

    def result(self, state, action):
        if not self.is_legal(state, action) or self.is_terminal(state)[0]:
            raise ValueError("Illegal move")
        
        # Copie de la grille
        board = [list(row) for row in state]
        player = self.player_to_move(state)

        # Simulation de la gravité : trouver la ligne la plus basse vide dans cette colonne
        for r in range(self.rows - 1, -1, -1):
            if board[r][action] == self.blank:
                board[r][action] = player
                break

        return tuple(tuple(row) for row in board)

    def winner(self, state):
        """Vérifie s'il y a un alignement de 4 jetons (horizontal, vertical, diagonales)."""
        r_len = self.rows
        c_len = self.cols

        # 1. Horizontal
        for r in range(r_len):
            for c in range(c_len - 3):
                p = state[r][c]
                if p != self.blank and all(p == state[r][c + i] for i in range(1, 4)):
                    return p

        # 2. Vertical
        for r in range(r_len - 3):
            for c in range(c_len):
                p = state[r][c]
                if p != self.blank and all(p == state[r + i][c] for i in range(1, 4)):
                    return p

        # 3. Diagonale descendante (\)
        for r in range(r_len - 3):
            for c in range(c_len - 3):
                p = state[r][c]
                if p != self.blank and all(p == state[r + i][c + i] for i in range(1, 4)):
                    return p

        # 4. Diagonale montante (/)
        for r in range(3, r_len):
            for c in range(c_len - 3):
                p = state[r][c]
                if p != self.blank and all(p == state[r - i][c + i] for i in range(1, 4)):
                    return p

        return None

    def is_terminal(self, state):
        """True si la partie est gagnée ou si la grille est pleine (match nul)."""
        w = self.winner(state)
        if w is not None:
            return True, w

        # Vérifier si la grille est pleine (ligne du haut entièrement remplie)
        if all(cell != self.blank for cell in state[0]):
            return True, None

        return False, None

    def evaluate(self, state, player):
        """Évaluation basique à somme nulle.""" # à modifier !!
        w = self.winner(state)
        if w == player:
            return 1
        elif w is not None:
            return -1
        return 0

    def display(self, state):
        """Affichage console propre de la grille de Puissance 4."""
        symbols = {self.blank: '.', self.player1: 'X', self.player2: 'O'}
        print(" " + " ".join(str(i) for i in range(self.cols)))
        for ligne in state:
            print(" ".join(symbols.get(cell, str(cell)) for cell in ligne))
        print("-" * (self.cols * 2))