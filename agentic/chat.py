# agentic/chat.py
import asyncio
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient

# Prérequis :
# - Ollama doit être installé.
# - Le modèle utilisé doit être téléchargé au préalable
#   (par ex. : ollama pull qwen3:8b).
#
# Exécution :
# 1. Lancer le serveur MCP dans un premier terminal :
#    python -m agentic.mcp_server
#
# 2. Lancer ce client dans un second terminal :
#    python -m agentic.chat
#
# Le serveur MCP doit rester actif pendant toute la session.

# SYSTEM = """Tu es AUSSI, un assistant qui joue au morpion (tictactoe) et au puissance 4 (connect4) avec l'utilisateur.
# Règles :
# - Ne calcule JAMAIS un coup toi-même et n'invente jamais l'état du plateau : utilise les outils.
# - Au début, appelle new_game, puis réutilise TOUJOURS le game_id retourné.
# - Si le jeu ou le coup n'est pas clair, demande une précision à l'utilisateur au lieu de deviner.
# - Si un outil retourne une erreur, lis-la et corrige ton appel.
# - Réponds brièvement en français, en montrant le plateau (board_text) tel quel."""

SYSTEM = """
Tu es AUSSI.

Utilise les outils pour gérer les parties.
N'invente jamais l'état du jeu.
Réponds brièvement en français, en montrant le plateau si nécessaire.
"""

# --- juste pour l'ui ---
async def spinner():
    while True:
        for c in "|/-\\":
            print(f"\r🧠 AUSSI réfléchit... {c}", end="", flush=True)
            await asyncio.sleep(0.1)


async def main():
    # 1) Connexion au serveur MCP lancé dans l'autre terminal
    client = MultiServerMCPClient({
        "aussi": {"transport": "streamable_http", "url": "http://127.0.0.1:8000/mcp"}
    })
    tools = await client.get_tools()       # récupère les outils + leurs JSON Schema
    print("Outils chargés :", [t.name for t in tools]) # debug de la liste des outils

    # 2) Le modèle local. temperature=0 => choix d'outils plus stables ?
    llm = ChatOllama(
        model="qwen3:8b", 
        reasoning=False,
        temperature=0,
        num_thread=14,
        num_ctx=2048
        )

    # resp = llm.invoke("Dis bonjour")
    # print(resp)

    # 3) La boucle agentique (LLM -> tool call -> résultat -> LLM ...) est gérée par create_agent
    agent = create_agent(llm, tools, system_prompt=SYSTEM)

    messages = [] # l'historique complet de la conversation, qu'on repasse à chaque tour
    while True:
        # lecture du message utilisateur
        user = input("\nToi > ")

        # commande de sortie
        if user.strip().lower() in {"quit", "exit"}:
            break

        # on retient la taille actuelle de l'historique.
        # cela permettra plus tard d'identifier uniquement les nouveaux messages générés pendant ce tour.
        before = len(messages)

        # Ajout du message utilisateur à l'historique
        messages.append(
            {
            "role": "user", 
            "content": user
            }
        )

        # Exécution de l'agent :
        # - le LLM analyse la requête
        # - décide éventuellement d'appeler un ou plusieurs outils
        # - récupère leur résultat
        # - génère une réponse finale
        messages = messages[-10:]

        # spin = asyncio.create_task(spinner())
        final_state = None
        try:
            # https://reference.langchain.com/python/langchain-core/runnables/base/Runnable/astream_events
            async for event in agent.astream_events(
                {"messages": messages},
                version="v2"
            ):
                event_name = event["event"]

                if event_name == "on_chat_model_start":
                    print("🧠  AUSSI réfléchit...")

                elif event_name == "on_tool_start":
                    print(f"🔧  Utilisation de : {event['name']}")

                elif event_name == "on_tool_end":
                    print("📥  Résultat reçu")

                elif event_name == "on_chat_model_end":
                    print("✍️  Génération de la réponse...")

                elif event_name == "on_chain_end":
                    final_state = event["data"].get("output")

        finally:
            # spin.cancel()
            print("\r" + " " * 40 + "\r", end="")

        if final_state:
            messages = final_state["messages"]
        
        # out = await agent.ainvoke({"messages": messages})
        # messages = out["message"]
        # print(out)

        # Debug : on affiche les appels d'outils du dernier tour
        # for m in messages[before:]:
        #     if getattr(m, "type", "") == "ai" and getattr(m, "tool_calls", None):
        #         for tc in m.tool_calls:
        #             print(f"  [tool call] {tc['name']}({tc['args']})")

        # Le dernier message de l'historique correspond normalement à la réponse finale
        print("\nAUSSI >\n", messages[-1].content)


if __name__ == "__main__":
    asyncio.run(main())