# test_engine.py : doit marcher avant de toucher au LLM
from agentic import engine

# Morpion : l'humain prend le centre
v = engine.start_game("tictactoe", True, "minimax")
print(v.board_text)
v = engine.play_human_turn(v.game_id, 2, 2)
print(v.board_text, "\n", v.message, "\n", v.ai_stats)

# Coup illégal : doit lever ValueError avec la liste des coups légaux
try:
    engine.play_human_turn(v.game_id, 2, 2)
except ValueError as e:
    print("OK, erreur attendue :", e)

# Puissance 4 : l'humain joue la colonne 4
v = engine.start_game("connect4", True, "minimax")
v = engine.play_human_turn(v.game_id, None, 4)   # row ignoré pour le puissance 4
print(v.board_text, "\n", v.message)
print(engine.suggest(v.game_id))