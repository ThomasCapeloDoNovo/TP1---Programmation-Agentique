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
        self.fcteval = EvalConnectFour(blank = self.blank)

        self._order = self._build_order()
    
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

    def _build_order(self):
        """Ordre centre vers bords, valide pour tout nombre de colonnes."""
        mid_left = (self.cols - 1) // 2
        order = []
        for distance in range(self.cols):
            left = mid_left - distance
            right = mid_left + 1 + distance
            if 0 <= left < self.cols and left not in order:
                order.append(left)
            if 0 <= right < self.cols and right not in order:
                order.append(right)
        return tuple(order)

    def actions(self, state):
        """Une action est valide si la case tout en haut de la colonne est vide."""
        # permet normalement d'améliorer l'alpha-beta -> coups centraux généralement meilleurs
        return [
            col for col in self._order
            if state[0][col] == self.blank
        ]

    def is_legal(self, state, action):
        if not isinstance(action, int) or action < 0 or action >= self.cols:
            return False
        return state[0][action] == self.blank

    def result(self, state, action):
        if not self.is_legal(state, action) or self.is_terminal(state):
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
        """Retourne True si la partie est gagnée ou si la grille est pleine."""
        if self.winner(state) is not None:
            return True
        return all(cell != self.blank for cell in state[0])

    def evaluate(self, state, player):
        """Évaluation"""
        return self.fcteval.get_eval(state, player)

    def display(self, state):
        """Affichage console propre de la grille de Puissance 4."""
        symbols = {self.blank: '.', self.player1: 'X', self.player2: 'O'}
        print(" " + " ".join(str(i) for i in range(self.cols)))
        for ligne in state:
            print(" ".join(symbols.get(cell, str(cell)) for cell in ligne))
        print("-" * (self.cols * 2))



class EvalConnectFour:
    def __init__(self, poids = None, poidscol= None, blank = 0):
        self.poids = poids if poids is not None else {
                1: 0,
                2: 100,
                3: 1000,
                4: 100000,
            }
        self.poidscol = poidscol if poidscol is not None else [2, 6, 9, 16, 9, 6, 2]
        self.blank = blank

        self._dims = None
        self._fenetres = []

    def _get_fenetres(self, rows, cols):
        """Liste des fenêtres de 4 cases (horizontales et diagonales), calculée une seule fois."""
        if self._dims != (rows, cols):
            fen = []
            for r in range(rows):
                for c in range(cols):
                    for dr, dc in ((0, 1), (1, 1), (-1, 1)):   # -, \, /
                        r_end, c_end = r + 3 * dr, c + 3 * dc
                        if 0 <= r_end < rows and 0 <= c_end < cols:
                            fen.append(tuple((r + i * dr, c + i * dc) for i in range(4)))
            self._fenetres = fen
            self._dims = (rows, cols)
        return self._fenetres
    
    def get_eval(self, grille, player):

        score = 0

        # verticale 
        for col in range(len(grille[0])):
            # récupère la premier case vide
            ligne = self._trouver_case_vide(grille, col)
            # récupère le score verticale
            score += self._evaluer_verticale(grille, ligne, col, player)

        # horizontale + diagonales : toutes les fenêtres
        lis_fen = self._get_fenetres(len(grille), len(grille[0]))
        for fenetre in lis_fen:
            moi = adv = 0
            for r, c in fenetre:
                v = grille[r][c]
                if v == self.blank:
                    continue
                if v == player:
                    moi += 1
                else:
                    adv += 1

            if moi and adv: # fenêtre bloquée
                continue
            if moi:
                score += self.poids[moi]
            elif adv:
                score -= 1.01 * self.poids[adv]

        return score


    def _trouver_case_vide(self, grille, colonne):
        # retourne -1 si la colonne est pleine

        if grille[0][colonne] != self.blank:
            return -1

        for ligne in range(1, len(grille)):
            if grille[ligne][colonne] != self.blank:
                return ligne - 1

        # pas de pion
        return len(grille) - 1

    # eval verti
    def _evaluer_verticale(self, grille, ligne, colonne, player):
        # pas de pion dans la colonne
        if ligne == len(grille) - 1:
            return 0

        # récupère la couleur du premier pion
        color = grille[ligne + 1][colonne]

        # on compte le nb de pion de la même couleur directement à côté
        nb = 1
        c_ligne = ligne + 2

        while c_ligne < len(grille) and nb < 4 and grille[c_ligne][colonne] == color:
            nb += 1
            c_ligne += 1

        # on compte le nb de place libre au dessus
        nbl = 0
        c_ligne = ligne
        
        while c_ligne >= 0 and nbl < 4 - nb and grille[c_ligne][colonne] == self.blank:
            nbl += 1
            c_ligne -= 1

        if nb + nbl >= 4:
            if nb == 1:
                # favorise le centre si il n'y a qu'un pion
                return (1 if player == color else - 1.01) * self.poidscol[colonne]
            else:
                return self.poids[nb] * (1 if player == color else - 1.01)
        else:
            return 0