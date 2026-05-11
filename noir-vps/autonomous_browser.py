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
    def explore_topic(topic: str):
        """Metode sinkron untuk dipanggil oleh Brain PC."""
        return asyncio.run(AutonomousBrowser._search_and_absorb(topic))

if __name__ == "__main__":
    AutonomousBrowser.explore_topic("Advanced Python optimization techniques")
