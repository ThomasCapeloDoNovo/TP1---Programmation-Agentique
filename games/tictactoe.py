
from game import Game

class TicTacToe(Game):
    """TicTacToe

    état  : tuple de tuple 3*3
    actions : (x, y)

    """


    def __init__(self, player1 = 1, player2 = 2):
        super().__init__(player1, player2)
        self.blank = 0
    
    def initial_state(self):
        return tuple(tuple(self.blank for _ in range(3)) for _ in range(3))

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
        """Une action est valide si la case est vide."""
        actions = []

        for id_ligne, ligne in enumerate(state):
            for id_col, col in enumerate(ligne):
                if col == self.blank:
                    actions.append((id_ligne, id_col))

        return actions

    def is_legal(self, state, action):
        ligne, col = action
        return state[ligne][col] == self.blank

    def result(self, state, action):
        if not self.is_legal(state, action) or self.is_terminal(state)[0]:
            raise ValueError("Illegal move")
            return state
        
        ligne, col = action
        player = self.player_to_move(state)
        board = [list(row) for row in state]
        board[ligne][col] = player
        return tuple(tuple(row) for row in board)

    def winner(self, state):
        """Retourne le joueur gagnant (player1 ou player2), ou None s'il n'y a pas de gagnant."""
        lines = []

        #lignes
        for ligne in state:
            lines.append(ligne)

        #colonnes
        for id_col in range(len(state[0])):
            lines.append(tuple(
                state[id_li][id_col] for id_li in range(len(state))
            ))

        #diagonales
        lines.append(tuple(
            state[i][i] for i in range(len(state))
        ))

        lines.append(tuple(
            state[i][len(state) - i - 1] for i in range(len(state))
        ))

        # vérif des lignes gagnantes 
        for line in lines:
            if line[0] != self.blank and all(cell == line[0] for cell in line):
                return line[0]

        return None
        

    def is_terminal(self, state):
        """True si le jeu est fini (gagnant ou grille pleine)."""
        w = self.winner(state)
        if w is not None:
            return True, w

        for ligne in state:
            if self.blank in ligne:
                return False, None

        return True, None

    def evaluate(self, state, player):
        """retourne l'evaluation de l'état pour le jouer player"""
        # ici à somme nulle
        w = self.winner(state)
        if w == player:
            return 1
        elif w is not None:
            return -1
        return 0

    def display(self, state):
        """Affichage console d'un état """
        symbols = {self.blank: '.', self.player1: 'X', self.player2: 'O'}
        for ligne in state:
            print(" ".join(symbols.get(cell, str(cell)) for cell in ligne))
        print()
