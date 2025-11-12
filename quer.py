import datetime
import queue
import threading
import logging
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM  # type: ignore
from langchain.callbacks.base import BaseCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from get_embedding_function_copy import get_embedding_function
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import FAISS_DIR, SPECIAL_KEYWORDS, LOGS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(LOGS_DIR, 'quer.log'),
    filemode='w'
)

# --- CONFIG ---
PROMPT_TEMPLATE = """
You are Etheg, a helpful assistant for NNRG college. Your primary goal is to provide accurate and concise answers based on the provided context.
When asked for the 'head' or 'HOD' of a department, you must prioritize searching for and using documents that explicitly contain the title "Head of Department" or "HOD".
If the context does not contain the answer to the question, state that you do not have enough information to answer. Do not make up information.
Use the conversation history to understand the user's intent and follow-up questions.

Conversation history:
{history}

Context:
{context}

Question: {question}

Answer:
"""

# --- In‐memory store of ConversationBufferMemory per session ---
_memory_store: dict[str, ConversationBufferMemory] = {}

def get_memory(session_id: str) -> ConversationBufferMemory:
    if session_id not in _memory_store:
        _memory_store[session_id] = ConversationBufferMemory(memory_key="chat_history")
    return _memory_store[session_id]

# --- Streaming Callback Handler ---
class StreamingQueueCallbackHandler(BaseCallbackHandler):
    def __init__(self, q: queue.Queue, memory: ConversationBufferMemory, user_query: str):
        self.q = q
        self.memory = memory
        self.buffer = ""
        # record the user’s turn
        self.memory.chat_memory.add_user_message(user_query)

    def on_llm_new_token(self, token: str, **kwargs):
        self.q.put(token)
        self.buffer += token

    def on_llm_end(self, response: any, **kwargs):
        # record the assistant’s turn
        self.memory.chat_memory.add_ai_message(self.buffer)
        self.q.put(None)

    def on_llm_error(self, error: BaseException, **kwargs):
        logging.error(f"LLM Error: {error}")
        self.q.put(None)

# --- Load FAISS index once ---
logging.info("🔧 Loading embedding function and FAISS index...")
try:
    embedding_function = get_embedding_function()
    db = FAISS.load_local(
        FAISS_DIR,
        embeddings=embedding_function,
        allow_dangerous_deserialization=True
    )
    csv_ids = [doc_id for doc_id, doc in db.docstore._dict.items() if doc.metadata.get("source") == "faculty_data.csv"]
    logging.info(f"✅ FAISS index loaded. {len(csv_ids)} CSV rows available.")
except Exception as e:
    logging.error(f"❌ Failed loading FAISS: {e}")
    db = None
    csv_ids = []

def is_special_query(query: str) -> bool:
    return any(k in query.lower() for k in SPECIAL_KEYWORDS)

# --- Main entrypoint with context support ---
def stream_query_agent(query_text: str, token_queue: queue.Queue, session_id: str):
    """
    Launches a background thread that streams LLM tokens into token_queue,
    while preserving conversation history in memory.
    """
    logging.info(f"🔍 Session {session_id} Received query: {query_text}")
    memory = get_memory(session_id)
    handler = StreamingQueueCallbackHandler(token_queue, memory, query_text)

    # Build the history string
    history_pieces = []
    for msg in memory.chat_memory.messages:
        if isinstance(msg, HumanMessage):
            history_pieces.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            history_pieces.append(f"Assistant: {msg.content}")
    history = "\n".join(history_pieces)

    # Determine RAG context
    ctx = ""
    if db:
        # Always search the full index for context
        ctx = _search_full(query_text)

    # Format prompt with history + context + question
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE).format(
        history=history,
        context=ctx,
        question=query_text
    )

    # Load the streaming LLM and invoke
    try:
        llm = OllamaLLM(model="nnrgbot", streaming=True, callbacks=[handler])
    except Exception as e:
        logging.error(f"❌ Ollama load error: {e}")
        token_queue.put(f"Error: could not load LLM: {e}")
        token_queue.put(None)
        return

    threading.Thread(target=lambda: llm.invoke(prompt), daemon=True).start()

def _search_full(query_text: str, score_threshold: float = 1.2) -> str:
    """
    Searches the entire FAISS index and filters results by a relevance score threshold.
    Lower scores are better (more relevant).
    """
    if not db:
        return "Vector database is not available."
    try:
        # Retrieve documents with their relevance scores
        results_with_scores = db.similarity_search_with_score(query_text, k=5)

        # Filter results based on the score threshold
        filtered_results = [doc for doc, score in results_with_scores if score < score_threshold]

        if not filtered_results:
            logging.info(f"ℹ️ No results for '{query_text}' met the score threshold of {score_threshold}.")
            return "No relevant context found."

        logging.info(f"ℹ️ Found {len(filtered_results)} relevant documents for '{query_text}'.")
        return "\n\n---\n\n".join(doc.page_content for doc in filtered_results)
    except Exception as e:
        logging.warning(f"⚠️ Full search error: {e}")
        return "Error during context retrieval."
