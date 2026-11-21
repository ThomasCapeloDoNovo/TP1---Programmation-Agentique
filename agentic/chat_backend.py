# agentic/chat_backend.py
"""
Backend du chat AUSSI pour l'interface pygame.

pygame tourne dans un thread synchrone, alors que l'agent LangChain est async.
On fait donc vivre l'agent dans un thread à lui, avec sa propre boucle asyncio.
La communication se fait par une queue thread-safe :

    UI  --send(texte)-->  backend
    UI  <--events.get_nowait()--  backend

Événements produits (kind, payload) :
    ("status", "Utilisation de : new_game")
    ("answer", "texte de la réponse")
    ("error",  "message d'erreur")
    ("done",   None)                      # fin du tour, dans tous les cas
"""
import asyncio
import queue
import threading

from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient

MCP_URL = "http://127.0.0.1:8000/mcp"
MODEL = "qwen3:8b"
MAX_HISTORY = 10

SYSTEM = """
Tu es AUSSI.

Utilise les outils pour gérer les parties.
N'invente jamais l'état du jeu.
Réponds brièvement en français.
Montre toujours le plateau dans un bloc de code (```).
"""


class ChatBackend:
    def __init__(self):
        self.events = queue.Queue()
        self._messages = []
        self._agent = None

        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    # ---------- API publique (appelée depuis le thread pygame) ----------

    def send(self, text: str):
        asyncio.run_coroutine_threadsafe(self._ask(text), self._loop)

    def reset(self):
        """Reset complet : historique vidé, événements en attente jetés, agent reconstruit
        (nouvelle connexion MCP + rechargement des outils au prochain message).
        À n'appeler que si aucun tour n'est en cours."""
        asyncio.run_coroutine_threadsafe(self._reset(), self._loop).result(timeout=5)

    def ask_sync(self, text: str):
        """Version bloquante pour le CLI : génère les événements (kind, payload) jusqu'à "done"."""
        self.send(text)
        while True:
            kind, payload = self.events.get()
            yield kind, payload
            if kind == "done":
                return

    # ---------- Interne (thread asyncio) ----------

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _reset(self):
        self._messages = []
        self._agent = None
        while True:
            try:
                self.events.get_nowait()
            except queue.Empty:
                break

    async def _ensure_agent(self):
        if self._agent is not None:
            return

        self.events.put(("status", "Connexion au serveur MCP"))
        try:
            client = MultiServerMCPClient({
                "aussi": {"transport": "streamable_http", "url": MCP_URL}
            })
            tools = await client.get_tools()
        except Exception as e:
            raise RuntimeError(
                "Serveur MCP injoignable. Lance-le dans un autre terminal :\n"
                "python -m agentic.mcp_server\n"
                f"({type(e).__name__})"
            ) from e

        llm = ChatOllama(
            model=MODEL,
            reasoning=False,
            temperature=0,
            num_thread=14,
            num_ctx=2048,
        )
        self._agent = create_agent(llm, tools, system_prompt=SYSTEM)

    async def _ask(self, text: str):
        try:
            await self._ensure_agent()

            self._messages.append({"role": "user", "content": text})
            self._messages = self._messages[-MAX_HISTORY:]

            self.events.put(("status", "AUSSI réfléchit"))
            final_state = None

            async for event in self._agent.astream_events(
                {"messages": self._messages}, version="v2"
            ):
                name = event["event"]

                if name == "on_chat_model_start":
                    self.events.put(("status", "AUSSI réfléchit"))
                elif name == "on_tool_start":
                    self.events.put(("status", f"Utilisation de : {event['name']}"))
                elif name == "on_tool_end":
                    self.events.put(("status", "Résultat reçu"))
                elif name == "on_chat_model_end":
                    self.events.put(("status", "Génération de la réponse"))
                elif name == "on_chain_end":
                    out = event["data"].get("output")
                    # On ne garde que l'état final (dict contenant "messages")
                    if isinstance(out, dict) and "messages" in out:
                        final_state = out

            if final_state:
                self._messages = final_state["messages"]

            answer = self._messages[-1].content if self._messages else ""
            if isinstance(answer, list):  # certains modèles renvoient des blocs
                answer = "".join(
                    b.get("text", "") if isinstance(b, dict) else str(b) for b in answer
                )
            self.events.put(("answer", answer or "(réponse vide)"))

        except Exception as e:
            self.events.put(("error", str(e)))
        finally:
            self.events.put(("done", None))