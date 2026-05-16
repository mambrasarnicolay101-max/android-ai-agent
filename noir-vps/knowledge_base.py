import os, json, logging
import numpy as np
try:
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    SentenceTransformer = None
    faiss = None

from security_guard import QueryGuard, SecurityBreachException

log = logging.getLogger("KnowledgeBase")
STORE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge", "vector_store")
os.makedirs(STORE_DIR, exist_ok=True)

class NeuralKnowledgeBase:
    """RAG System: Local vector store for 'Infinite Memory' on 4GB RAM."""
    _model = None
    _index = None
    _metadata = [] # List of text chunks

    @classmethod
    def _init_model(cls):
        if cls._model is None and SentenceTransformer:
            log.info("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            cls._dim = 384
            cls._index = faiss.IndexFlatL2(cls._dim)
            cls._load_existing()

    @classmethod
    def _load_existing(cls):
        meta_path = os.path.join(STORE_DIR, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                cls._metadata = json.load(f)
            # Re-index everything (since IndexFlatL2 is small)
            if cls._metadata:
                embeddings = cls._model.encode(cls._metadata)
                cls._index.add(np.array(embeddings).astype('float32'))
                log.info(f"Loaded {len(cls._metadata)} chunks into local memory.")

    @classmethod
    def add_knowledge(cls, text: str):
        try:
            text = QueryGuard.sanitize(text)
        except SecurityBreachException as e:
            log.error(f"Failed to add knowledge: {e}")
            return

        cls._init_model()
        if not text or not cls._model: return
        
        # Simple chunking
        chunks = [text[i:i+500] for i in range(0, len(text), 400)]
        embeddings = cls._model.encode(chunks)
        cls._index.add(np.array(embeddings).astype('float32'))
        cls._metadata.extend(chunks)
        
        # Save metadata
        with open(os.path.join(STORE_DIR, "metadata.json"), "w") as f:
            json.dump(cls._metadata, f)
        log.info(f"Added {len(chunks)} new knowledge chunks.")

    @classmethod
    def query(cls, question: str, top_k: int = 3):
        try:
            question = QueryGuard.sanitize(question)
        except SecurityBreachException as e:
            log.error(f"Query blocked: {e}")
            return "SECURITY_ALERT: Malicious pattern detected in query."

        cls._init_model()
        if not cls._model or cls._index.ntotal == 0: return ""
        
        q_emb = cls._model.encode([question])
        D, I = cls._index.search(np.array(q_emb).astype('float32'), top_k)
        
        results = []
        for idx in I[0]:
            if idx != -1 and idx < len(cls._metadata):
                results.append(cls._metadata[idx])
        
        return "\n---\n".join(results)

# Initialize on import if possible
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    NeuralKnowledgeBase.add_knowledge("Noir Sovereign v18.4 is the latest version with 4GB RAM support.")
    print("Query Result:", NeuralKnowledgeBase.query("What is the latest version?"))
