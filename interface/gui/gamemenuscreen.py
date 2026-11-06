import pygame
import time
import threading
import copy

from .widgets import Button, Selector, VerticalSelector, NumberInput
from . import theme as T
from .renderersgames import get_game_renderer

from games.tictactoe import TicTacToe
from games.connectfour import ConnectFour
from games.agents.humainagent import HumanAgent
from games.agents.randomagent import RandomAgent
from games.agents.minimaxagent import MinimaxAgent
from games.agents.mctsagent import MCTSAgent



W, H = 1100, 720
LIMITS = dict(max_expansions=300_000, max_time=10.0)
ROW_H = 24

LI_GAME = {
    "tictactoe" : {"title" : "Tic-Tac-Toe (3x3)", "game" : TicTacToe},
    "connect4" : {"title": "Puissance 4 (6x7)", "game" : ConnectFour}
} 

LI_AGENT = {
    "human" : {"title" : "Humain", "agent" : HumanAgent},
    "random" : {"title" : "Aléatoire", "agent" : RandomAgent},
    "minimax" : {"title" : "Minimax (IDS + Alpha-Beta)", "agent" : MinimaxAgent},
    "mcts" : {"title" : "MCTS", "agent" : MCTSAgent},

}


class GameMenuScreen:
    def __init__(self, app):
        self.app = app
        x, w = 60, W - 120
        
        # Choix du jeu
        self.game_selector = Selector("Jeu", x, 95, w, 
            [[b, li["title"]] for b, li in list(LI_GAME.items())]
        )
        
        # Configuration Joueur 1 & Joueur 2 (2 colonnes)
        agent_options = [[b, li["title"]] for b, li in list(LI_AGENT.items())]

        col_w = w // 2 - 15
        
        # Configuration Joueur 1 (Colonne de gauche)
        self.p1_selector = VerticalSelector("Joueur 1 (X)", x, 170, col_w, agent_options, "human")
        
        self.p1_depth = NumberInput(
            "Profondeur max",
            x,
            380,
            120,
            default_value=5,
            min_value=1,
            max_value=20
        )

        self.p1_time = NumberInput(
            "Temps (s)",
            x,
            450,
            120,
            default_value=1.0,
            min_value=0.1,
            max_value=60,
            allow_float=True
        )

        # Configuration Joueur 2 (Colonne de droite)
        self.p2_selector = VerticalSelector("Joueur 2 (O)", x + col_w + 30, 170, col_w, agent_options, "minimax")
        
        self.p2_depth = NumberInput(
            "Profondeur",
            x + col_w + 30,
            380,
            120,
            default_value=5,
            min_value=1,
            max_value=20
        )

        self.p2_time = NumberInput(
            "Temps (s)",
            x + col_w + 30,
            450,
            120,
            default_value=1.0,
            min_value=0.1,
            max_value=60,
            allow_float=True
        )
        
        self.launch = Button((x, 550, 240, 52), "Lancer la Partie", self.start_game)
        self.back_btn = Button((x, 610, 240, 48), "Retour Menu Principal", self.back_to_main)

    def start_game(self):
        # Instanciation du jeu choisi
        game_key = self.game_selector.selected
        game_inst = LI_GAME[game_key]["game"]()

        # Factory d'agents
        def build_agent(agent_type, name, depth = 3, time_lim = 1):
            if agent_type in LI_AGENT:
                # !! modif
                if agent_type == "minimax":
                    return MinimaxAgent(
                        max_depth=depth,
                        time_limit=time_lim,
                        name=name
                    )

                # !! 
                if agent_type == "mcts":
                    return MCTSAgent(
                        time_limit=time_lim,
                        name=name
                    )

                return LI_AGENT[agent_type]["agent"](name)
            
            return RandomAgent(name)

        agent1 = build_agent(
            self.p1_selector.selected,
            "Joueur 1",
            self.p1_depth.int_value,
            self.p1_time.float_value
        )

        agent2 = build_agent(
            self.p2_selector.selected,
            "Joueur 2",
            self.p2_depth.int_value,
            self.p2_time.float_value
        )

        self.app.screen_obj = GameRunScreen(self.app, game_key, game_inst, agent1, agent2)

    def back_to_main(self):
        from.app import MenuScreen
        self.app.screen_obj = MenuScreen(self.app)

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.game_selector.click(ev.pos)
            self.p1_selector.click(ev.pos)
            self.p2_selector.click(ev.pos)

            if self.p1_selector.selected == "minimax":
                self.p1_depth.handle(ev)
                self.p1_time.handle(ev)

            elif self.p1_selector.selected == "mcts":
                self.p1_time.handle(ev)

            if self.p2_selector.selected == "minimax":
                self.p2_depth.handle(ev)
                self.p2_time.handle(ev)

            elif self.p2_selector.selected == "mcts":
                self.p2_time.handle(ev)

            self.launch.click(ev.pos)
            self.back_btn.click(ev.pos)
        elif ev.type == pygame.KEYDOWN:

            if self.p1_selector.selected == "minimax":
                self.p1_depth.handle(ev)
                self.p1_time.handle(ev)
            elif self.p1_selector.selected == "mcts":
                self.p1_time.handle(ev)

            if self.p2_selector.selected == "minimax":
                self.p2_depth.handle(ev)
                self.p2_time.handle(ev)
            elif self.p2_selector.selected == "mcts":
                self.p2_time.handle(ev)

            if ev.key == pygame.K_ESCAPE:
                self.back_to_main()

    def update(self, dt):
        pass

    def draw(self, surf):
        surf.fill(T.BG)
        T.draw_text(surf, "AUSSI V3.0 - Jeux Adversariaux", (60, 30), 54, T.ACCENT, bold=True)
        T.draw_text(surf, "Moteur de décision générique (Minimax & MCTS)", (60, 75), 26, T.MUTED)
        
        self.game_selector.draw(surf)
        self.p1_selector.draw(surf)
        self.p2_selector.draw(surf)
        self.launch.draw(surf)
        self.back_btn.draw(surf)
        if self.p1_selector.selected == "minimax":
            self.p1_depth.draw(surf)
            self.p1_time.draw(surf)

        elif self.p1_selector.selected == "mcts":
            self.p1_time.draw(surf)

        if self.p2_selector.selected == "minimax":
            self.p2_depth.draw(surf)
            self.p2_time.draw(surf)

        elif self.p2_selector.selected == "mcts":
            self.p2_time.draw(surf)



class GameRunScreen:
    BOARD_RECT = pygame.Rect(20, 80, 680, 620)
    PANEL_RECT = pygame.Rect(720, 80, 360, 620)

    def __init__(self, app, game_key, game_instance, agent1, agent2):
        self.app = app
        self.game_key = game_key
        self.game = game_instance
        self.state = self.game.initial_state()
        
        # Association des joueurs (player1, player2) à leurs agents
        self.agents = {
            self.game.player1: agent1,
            self.game.player2: agent2
        }
        
        self.renderer = get_game_renderer(self.game)

        self.menu_btn = Button((1100 - 190, 22, 170, 40), "Menu (Échap)", self.back_to_menu)
        
        self.game_over = False
        self.winner = None
        self.ai_thinking = False
        
        # Stockage des dernières métriques de l'agent pour le panneau latéral
        self.last_agent_stats = "En attente du premier coup..."

        self.ai_thread = None
        self.pending_ai_results = None

    def back_to_menu(self):
        self.app.screen_obj = GameMenuScreen(self.app)

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.menu_btn.click(ev.pos):
                return

        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.back_to_menu()
            
        if self.game_over:
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                # Relancer une partie
                self.state = self.game.initial_state()
                self.game_over = False
                self.winner = None
                self.last_agent_stats = "Nouvelle partie démarrée."
            return

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:

            # Gestion du clic pour l'agent Humain
            current_player = self.game.player_to_move(self.state)
            current_agent = self.agents[current_player]
            
            # On vérifie si c'est un agent humain et qu'il n'est pas en train de "réfléchir" (IA)
            if isinstance(current_agent, HumanAgent) and not self.ai_thinking:
                action = self.get_action_from_click(ev.pos)
                if action is not None and self.game.is_legal(self.state, action):
                    self.state = self.game.result(self.state, action)
                    self.check_game_state()



    def get_action_from_click(self, pos):
        """Convertit un clic de souris sur BOARD_RECT en action valide selon le jeu."""
        if not self.BOARD_RECT.collidepoint(pos):
            return None

        return self.renderer.get_action_from_click(pos, self.BOARD_RECT, self.game, self.state)

    def compute_ai_move(self, current_player, current_agent, state):
        start_t = time.perf_counter()

        action = current_agent.get_move(
            self.game,
            state
        )

        elapsed = time.perf_counter() - start_t

        self.pending_ai_results = (
            action,
            elapsed,
            current_player,
            current_agent
        )

    def update(self, dt): # boucle de jeu / ~SEARCH
        self.check_game_state() # au cas où

        if self.game_over:
            return

        # une ia vient de finir sa recherche
        if self.pending_ai_results is not None:
            action, elapsed, current_player, current_agent = self.pending_ai_results
            if action is not None and self.game.is_legal(self.state, action):
                self.state = self.game.result(self.state, action)

                stats_lines = [
                    f"Joueur : {current_player}",
                    f"Agent : {current_agent.__class__.__name__}",
                    f"Coup : {action}",
                    f"Temps : {elapsed:.3f} s"
                ]

                if hasattr(current_agent, "last_completed_depth"):
                    stats_lines.append(
                        f"Profondeur IDS complétée : "
                        f"{current_agent.last_completed_depth} / {current_agent.max_depth}"
                    )

                if hasattr(current_agent, "nodes_explored"):
                    stats_lines.append(
                        f"Nœuds explorés : {current_agent.nodes_explored}"
                    )

                if hasattr(current_agent, "last_simulations_run"):
                    stats_lines.append(
                        f"Simulations : {current_agent.last_simulations_run}"
                    )

                self.last_agent_stats = "\n".join(stats_lines)

            self.pending_ai_results = None
            self.ai_thread = None
            self.ai_thinking = False

            self.check_game_state()
            return 

        if self.ai_thinking:
            return
        
        current_player = self.game.player_to_move(self.state)
        current_agent = self.agents[current_player]

        # Si le joueur actuel est une IA (Minimax, MCTS, Random), on récupère son coup automatiquement
        if not isinstance(current_agent, HumanAgent):
            self.ai_thinking = True
            state_snapshot = copy.deepcopy(self.state)
            # L'appel à l'agent se fait de manière générique via l'interface du jeu
            self.ai_thread = threading.Thread(
                target=self.compute_ai_move,
                args=(current_player, current_agent, state_snapshot),
                daemon=True
            )
            self.ai_thread.start()

    def check_game_state(self):
        is_term, utility = self.game.is_terminal(self.state)
        if is_term:
            self.game_over = True
            self.winner = utility  # utility contient le gagnant (player1/player2) ou None (match nul)

    def draw(self, surf):
        surf.fill(T.BG)
        
        # En-tête et Bouton Menu
        title = f"Partie en cours — {self.game.__class__.__name__}"
        T.draw_text(surf, title, (20, 30), 32, T.TEXT, bold=True)
        self.menu_btn.draw(surf)
        
        # Conteneurs visuels
        pygame.draw.rect(surf, T.PANEL, self.BOARD_RECT, border_radius=10)
        pygame.draw.rect(surf, T.PANEL, self.PANEL_RECT, border_radius=10)

        # 1. Dessin du plateau via le renderer adapté
        if self.renderer:
            self.renderer.draw(surf, self.BOARD_RECT.inflate(-20, -20), self.game, self.state)

        # 2. Dessin du panneau latéral (Infos du tour, métriques de l'IA)
        self.draw_side_panel(surf)


    def draw_side_panel(self, surf):
        x = self.PANEL_RECT.x + 20
        y = self.PANEL_RECT.y + 20
        w = self.PANEL_RECT.w - 45

        current_player = self.game.player_to_move(self.state)
        current_agent_name = self.agents[current_player]

        T.draw_text(surf, f"Tour : Joueur {current_player}", (x, y), 24, T.ACCENT, bold=True)
        y += 30
        T.draw_text(surf, f"Type : {current_agent_name.__class__.__name__}", (x, y), 19, T.MUTED)
        y += 40

        if self.ai_thinking:
            T.draw_text(surf, "L'IA réfléchit...", (x, y), 22, T.WARN, bold=True)
            y += 40

        # Section des statistiques d'explicabilité
        T.draw_text(surf, "Statistiques de recherche", (x, y), 22, T.TEXT, bold=True)
        y += 30

        for line in self.last_agent_stats.split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                T.draw_text(surf, key.strip() + " :", (x, y), 18, T.MUTED)
                T.draw_text(surf, val.strip(), (x + 140, y), 18, T.TEXT, bold=True)
            else:
                T.draw_text(surf, line, (x, y), 18, T.TEXT)
            y += 26

        # Affichage de fin de partie
        if self.game_over:
            y += 30
            pygame.draw.line(surf, T.PANEL_LIGHT, (x, y), (x + w, y), 1)
            y += 20
            
            if self.winner is not None:
                msg = f"Victoire du Joueur {self.winner} !"
                color = T.GOOD
            else:
                msg = "Match nul !"
                color = T.WARN
                
            T.draw_text(surf, msg, (x, y), 24, color, bold=True)
            y += 35
            T.draw_text(surf, "Appuyez sur [Entrée] pour rejouer", (x, y), 16, T.MUTED)