from .agent import Agent

class HumanAgent(Agent):
    """Agent contrôlé par un joueur humain."""
    def __init__(self, name="Humain"):
        super().__init__(name)

    def get_move(self, game, state):
        # pas utilisé, directement via pygame
        game.display(state)
        legal_actions = game.actions(state)
        print(f"[{self.name}] Actions légales : {legal_actions}")
        
        while True:
            try:
                user_input = input(f"[{self.name}] Entrez votre action (ex: 'x,y' pour Tic-Tac-Toe ou un entier 'col' pour Puissance 4) : ")
                
                # Parsing intelligent selon le format de l'action du jeu
                if "," in user_input:
                    action = tuple(map(int, user_input.split(",")))
                else:
                    action = int(user_input)
                
                if action in legal_actions:
                    return action
                else:
                    print("Action illégale ou invalide dans cette position. Réessayez.")
            except ValueError:
                print("Format incorrect. Utilisez 'x,y' ou un numéro de colonne entier.")

