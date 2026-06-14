import asyncio
import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from vector_memory import vector_memory

log = logging.getLogger("AutonomousBrowser")

class AutonomousBrowser:
    """Agen Web-Scraping otonom yang menjelajah literatur internet untuk belajar."""
    
    _last_screenshot = None
    _last_url = None
    _last_title = None
    _browser_instance = None
    _page_instance = None

    @staticmethod
    async def get_page():
        if AutonomousBrowser._page_instance is None:
            p = await async_playwright().start()
            browser = await p.chromium.launch(headless=True)
            AutonomousBrowser._page_instance = await browser.new_page()
        return AutonomousBrowser._page_instance

    @staticmethod
    async def navigate_to(url: str):
        """Navigasi manual dari dashboard."""
        log.info(f"[Browser] Navigasi ke: {url}")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, timeout=30000)
                
                AutonomousBrowser._last_url = url
                AutonomousBrowser._last_title = await page.title()
                
                # Ambil screenshot untuk Dashboard
                screenshot_bytes = await page.screenshot(type="jpeg", quality=60)
                import base64
                AutonomousBrowser._last_screenshot = base64.b64encode(screenshot_bytes).decode('utf-8')
                
                content = await page.evaluate("() => document.body.innerText")
                await browser.close()
                return {"url": url, "title": AutonomousBrowser._last_title, "screenshot": AutonomousBrowser._last_screenshot, "content": content[:2000]}
        except Exception as e:
            log.error(f"[Browser] Gagal navigasi: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_last_view():
        return {
            "url": AutonomousBrowser._last_url,
            "title": AutonomousBrowser._last_title,
            "screenshot": AutonomousBrowser._last_screenshot
        }
    @staticmethod
    async def _search_and_absorb(query: str):
        log.info(f"[Browser] Memulai ekspedisi pencarian: {query}")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Gunakan DuckDuckGo untuk mencari literatur tanpa blokir Google
                search_url = f"https://html.duckduckgo.com/html/?q={query}"
                await page.goto(search_url, timeout=15000)
                
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                results = []
                # Ambil hasil pencarian teratas
                for a in soup.find_all('a', class_='result__url', limit=3):
                    url = a.get('href')
                    if url and url.startswith("http"):
                        results.append(url)
                
                import transformers
                import warnings
                warnings.filterwarnings("ignore")
                
                # Menggunakan AI Lokal Sendiri (Local SLM) untuk memproses literatur secara mandiri & cepat
                log.info("[Local AI] Memuat model pemahaman teks lokal (CPU-Optimized)...")
                try:
                    summarizer = transformers.pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
                except Exception as e:
                    summarizer = None
                    log.warning(f"Gagal memuat Local AI: {e}")

                learned_content = []
                for url in results:
                    log.info(f"[Browser] Membaca literatur: {url}")
                    try:
                        await page.goto(url, timeout=15000)
                        text = await page.evaluate("() => document.body.innerText")
                        
                        # AI Murni Kita Sendiri yang Memahami (Bukan Gemini/Groq)
                        if summarizer and len(text) > 100:
                            # Potong teks agar muat di model lokal
                            chunk = text[:3000]
                            log.info("[Local AI] Menganalisis dan menyarikan makna literatur...")
                            summary_out = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
                            summary = summary_out[0]['summary_text']
                        else:
                            summary = text[:2000] 
                            
                        learned_content.append({"url": url, "text": summary})
                        
                        # Simpan ke Vector DB
                        vector_memory.add_experience(
                            text=f"Learned from {url}: {summary}",
                            metadata={"source": "browser_exploration", "topic": query, "ai_processed": "local_slm"}
                        )
                    except Exception as e:
                        log.warning(f"[Browser] Gagal membaca {url}: {e}")
                
                await browser.close()
                log.info(f"[Browser] Selesai menyerap {len(learned_content)} sumber web.")
                return learned_content
        except Exception as e:
            log.error(f"[Browser] Kerusakan Navigasi Otonom: {e}")
            return []

    @staticmethod
    async def deep_crawl(start_url: str, max_depth: int = 1, current_depth: int = 0, visited: set = None):
        """
        [THE SPIDER]
        Merayapi sebuah website secara otonom dari link ke link (DFS/BFS), 
        mengekstrak teksnya, dan menyimpannya di NoirSearchEngine.
        Murni menggunakan requests agar sangat ringan dan cepat (fallback Playwright).
        """
        import requests
        if visited is None:
            visited = set()

        # Normalisasi URL (hilangkan fragment)
        base_url = start_url.split('#')[0]
        if base_url in visited or current_depth > max_depth:
            return
            
        visited.add(base_url)
        log.info(f"[Spider] Mengunjungi (Depth {current_depth}/{max_depth}): {base_url}")
        
        try:
            # Gunakan requests biasa yang stabil di semua env Windows
            headers = {'User-Agent': 'Noir-Sovereign-Spider/1.0'}
            # Jalankan di thread executor agar tidak memblokir async loop
            loop = asyncio.get_event_loop()
            import functools
            resp = await loop.run_in_executor(None, functools.partial(requests.get, base_url, headers=headers, timeout=10))
            
            if resp.status_code != 200:
                log.warning(f"[Spider] HTTP {resp.status_code} pada {base_url}")
                return
                
            html_content = resp.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            title = soup.title.string if soup.title else base_url
            
            # Hapus tag script, style, dll
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.extract()
            content = soup.get_text(separator=' ', strip=True)
            
            # Simpan ke Search Engine Internal
            from noir_search_engine import NoirSearchEngine
            engine = NoirSearchEngine()
            engine.add_document(url=base_url, title=title, content=content)
            log.info(f"[Spider] Disimpan ke indeks: {title}")
            
            # Jika masih ada kedalaman tersisa, ekstrak link
            if current_depth < max_depth:
                links = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('http'):
                        links.append(href)
                    elif href.startswith('/'):
                        # Bangun URL absolut
                        from urllib.parse import urlparse
                        parsed_uri = urlparse(base_url)
                        root = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
                        links.append(root + href)
                        
                # Batasi jumlah cabang per halaman agar tidak eksponensial meledak
                import random
                if len(links) > 5:
                    links = random.sample(links, 5)
                
                for link in links:
                    await AutonomousBrowser.deep_crawl(link, max_depth, current_depth + 1, visited)
                     
        except Exception as e:
            log.warning(f"[Spider] Gagal merayapi {base_url}: {e}")

    @staticmethod
    def start_crawl_job(seed_url: str, depth: int = 1):
        """Metode sinkron untuk dipanggil oleh The Trinity."""
        log.info(f"\n======================================")
        log.info(f"[SPIDER] MEMULAI MISI CRAWLING MASIF")
        log.info(f"Target: {seed_url} | Depth: {depth}")
        log.info(f"======================================")
        asyncio.run(AutonomousBrowser.deep_crawl(seed_url, depth))

if __name__ == "__main__":
    # Test crawler
    AutonomousBrowser.start_crawl_job("https://en.wikipedia.org/wiki/Artificial_intelligence", depth=1)
