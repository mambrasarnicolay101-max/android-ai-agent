import os
import logging
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh.analysis import StemmingAnalyzer

log = logging.getLogger("NoirSearchEngine")
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class NoirSearchEngine:
    """
    [THE OMNISCIENT INDEX]
    Mesin pencari internal super cepat milik Noir Sovereign menggunakan Whoosh.
    Menyimpan jutaan teks hasil rayapan (crawl) untuk diakses secara offline.
    """

    def __init__(self, index_dir=".sandbox/search_index"):
        self.index_dir = os.path.join(os.path.dirname(__file__), index_dir)
        
        # Definisikan skema penyimpanan
        self.schema = Schema(
            url=ID(stored=True, unique=True),
            title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
            content=TEXT(stored=True, analyzer=StemmingAnalyzer())
        )
        
        # Buat atau buka index
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)
            self.ix = create_in(self.index_dir, self.schema)
            log.info(f"[SearchEngine] Indeks baru diciptakan di {self.index_dir}")
        else:
            if exists_in(self.index_dir):
                self.ix = open_dir(self.index_dir)
                log.info(f"[SearchEngine] Memuat indeks yang ada dari {self.index_dir}")
            else:
                self.ix = create_in(self.index_dir, self.schema)
                log.info(f"[SearchEngine] Indeks kosong diinisialisasi ulang di {self.index_dir}")

    def add_document(self, url: str, title: str, content: str):
        """Menambahkan halaman web baru ke dalam indeks pencarian Noir."""
        try:
            # Pastikan tipe data benar-benar string standar (hindari BeautifulSoup NavigableString recursion)
            safe_url = str(url)
            safe_title = str(title)
            safe_content = str(content)
            
            # Truncate content untuk menghindari recursion depth exceeded di Whoosh tokenization
            if len(safe_content) > 50000:
                safe_content = safe_content[:50000]
            
            writer = self.ix.writer()
            # Gunakan update_document agar URL yang sama ditimpa (tidak ganda)
            writer.update_document(url=safe_url, title=safe_title, content=safe_content)
            writer.commit()
            log.debug(f"[SearchEngine] Berhasil mengindeks: {safe_url}")
        except Exception as e:
            log.error(f"[SearchEngine] Gagal mengindeks {url}: {e}")

    def search(self, query_str: str, limit: int = 10):
        """Melakukan pencarian kilat di dalam memori internal."""
        log.info(f"[SearchEngine] Menerima kueri: '{query_str}'")
        results_data = []
        try:
            with self.ix.searcher() as searcher:
                query = QueryParser("content", self.ix.schema).parse(query_str)
                results = searcher.search(query, limit=limit)
                
                for r in results:
                    # Ambil cuplikan teks yang mengandung kata kunci (highlights)
                    snippet = r.highlights("content")
                    if not snippet:
                        snippet = r['content'][:200] + "..."
                        
                    results_data.append({
                        "url": r['url'],
                        "title": r['title'],
                        "snippet": snippet,
                        "score": r.score
                    })
            log.info(f"[SearchEngine] Ditemukan {len(results_data)} hasil lokal.")
            return results_data
        except Exception as e:
            log.error(f"[SearchEngine] Pencarian gagal: {e}")
            return []

if __name__ == "__main__":
    # Test sederhana
    engine = NoirSearchEngine()
    engine.add_document("http://internal.noir/1", "Dokumen Rahasia Noir", "Ini adalah teks rahasia yang berisi strategi evolusi AI otonom.")
    engine.add_document("http://internal.noir/2", "Tutorial Memasak", "Cara memasak nasi goreng enak dan lezat.")
    
    print("\n--- Uji Coba Kueri: 'evolusi AI' ---")
    res = engine.search("evolusi AI")
    for r in res:
        print(f"[{r['score']}] {r['title']} - {r['url']}\n{r['snippet']}\n")
