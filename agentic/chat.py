# agentic/chat.py
# Client CLI : réutilise exactement le même backend que l'interface pygame.
#
# Prérequis :
# - Ollama installé + modèle téléchargé (ex. : ollama pull qwen3:8b)
#
# Exécution :
# 1. Serveur MCP dans un premier terminal :   python -m agentic.mcp_server
# 2. Ce client dans un second terminal :      python -m agentic.chat
#
# Commandes : "reset" pour repartir de zéro, "quit" / "exit" pour sortir.
from agentic.chat_backend import ChatBackend

ICONS = (
    ("Connexion", "🔌"),
    ("Utilisation de", "🔧"),
    ("Résultat", "📥"),
    ("Génération", "✍️"),
    ("AUSSI réfléchit", "🧠"),
)


def icon(status: str) -> str:
    for prefix, ic in ICONS:
        if status.startswith(prefix):
            return ic
    return "•"


def main():
    backend = ChatBackend()
    print("AUSSI — 'reset' pour recommencer, 'quit' pour sortir.")

    while True:
        try:
            user = input("\nToi > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        cmd = user.lower()
        if cmd in {"quit", "exit"}:
            break
        if cmd == "reset":
            backend.reset()
            print("🔄  Conversation réinitialisée.")
            continue
        if not user:
            continue

        last = None
        for kind, payload in backend.ask_sync(user):
            if kind == "status":
                if payload != last:           # évite les répétitions
                    print(f"{icon(payload)}  {payload}...")
                    last = payload
            elif kind == "answer":
                print("\nAUSSI >\n" + payload)
            elif kind == "error":
                print(f"\n⚠️  {payload}")


if __name__ == "__main__":
    main()