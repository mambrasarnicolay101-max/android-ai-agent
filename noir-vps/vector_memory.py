import os
import time
import json
import logging

log = logging.getLogger("VectorMemory")

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False
    log.warning("ChromaDB not installed! Vector Memory will run in dummy mode.")

# FASE 2: Hyper-Cognition RAG
class VectorMemory:
    """Basis data vektor persisten menggunakan ChromaDB untuk ingatan tanpa batas."""
    
    def __init__(self):
        self.collection = None
        if not HAS_CHROMA:
            return
        
        try:
            db_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "chroma_db")
            os.makedirs(db_path, exist_ok=True)
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_or_create_collection(
                name="noir_sovereign_memory",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            log.error(f"Failed to init ChromaDB: {e}")
            self.collection = None

    def add_experience(self, text: str = None, metadata: dict = None, content: str = None, category: str = "general", source: str = "system"):
        if self.collection is None:
            return None
            
        if text is None and content is not None:
            text = content
            
        if not metadata:
            metadata = {}
        metadata["timestamp"] = time.time()
        if "category" not in metadata: metadata["category"] = category
        if "source" not in metadata: metadata["source"] = source
        
        # Gunakan embedding default Chroma (all-MiniLM-L6-v2)
        doc_id = f"mem_{int(time.time() * 1000)}"
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        return doc_id

    def index_evolution_history(self):
        """Indeks seluruh riwayat evolusi ke dalam memori vektor."""
        log.info("[MEMORY] Mengindeks riwayat evolusi...")
        evo_file = os.path.join(os.path.dirname(__file__), "..", "knowledge", "evolution", "evolution_history.json")
        if os.path.exists(evo_file):
            try:
                with open(evo_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    for item in history:
                        content = f"Mutasi Sistem: {item.get('title')}. {item.get('description')}"
                        self.add_experience(text=content, metadata={"type": "evolution", "id": item.get("id")})
                log.info(f"[MEMORY] {len(history)} mutasi sistem berhasil diindeks.")
            except Exception as e:
                log.error(f"[MEMORY] Gagal mengindeks evolusi: {e}")

    def index_chat_history(self, history_list):
        """Indeks riwayat percakapan untuk pemahaman konteks jangka panjang."""
        if not history_list: return
        log.info(f"[MEMORY] Mengindeks {len(history_list)} pesan percakapan...")
        for chat in history_list:
            role = chat.get("role", "user")
            msg = chat.get("msg", "")
            if msg:
                self.add_experience(text=f"{role.upper()}: {msg}", metadata={"type": "chat"})

    def query(self, text: str, n_results: int = 3):
        if self.collection is None:
            return []
            
        try:
            results = self.collection.query(
                query_texts=[text],
                n_results=n_results
            )
            if results["documents"] and len(results["documents"]) > 0:
                # Return list of strings
                return results["documents"][0]
            return []
        except Exception as e:
            log.error(f"[VectorMemory] Query Error: {e}")
            return []

vector_memory = VectorMemory()
