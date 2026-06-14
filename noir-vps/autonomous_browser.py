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
    def explore_topic(topic: str):
        """
        Mencari literatur di internet publik secara otonom lalu merayapinya 
        agar masuk ke dalam NoirSearchEngine.
        """
        import requests
        import urllib.parse
        
        # Ekstrak kata kunci inti jika topik terlalu panjang (untuk mempermudah mesin pencari)
        search_query = topic.split(':')[0] if ':' in topic else topic
        if len(search_query) > 50:
            search_query = search_query[:50]
            
        log.info(f"\n[Browser] Memulai ekspedisi pencarian publik: '{search_query}'")
        
        # Header Chrome standar untuk menghindari blokir anti-bot/SSL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        
        try:
            urls = []
            
            # 1. Coba Wikipedia API (Paling stabil, tanpa blokir SSL)
            search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(search_query)}&limit=3&namespace=0&format=json"
            resp = requests.get(search_url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 3 and data[3]:
                    urls = data[3]
                    log.info(f"[Browser] Ditemukan via Wikipedia: {len(urls)} URL")
            
            # 2. Jika Wikipedia kosong, Fallback ke Bing HTML Lite
            if not urls:
                log.info("[Browser] Wikipedia tidak menemukan hasil yang cocok, mencoba Bing HTML...")
                bing_url = f"https://www.bing.com/search?q={urllib.parse.quote(search_query)}"
                resp_bing = requests.get(bing_url, headers=headers, timeout=15)
                
                if resp_bing.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(resp_bing.text, 'html.parser')
                    for h2 in soup.find_all('h2'):
                        a = h2.find('a', href=True)
                        if a and a['href'].startswith("http") and "microsoft.com" not in a['href']:
                            urls.append(a['href'])
                            if len(urls) >= 3:
                                break
                                
            log.info(f"[Browser] Total {len(urls)} target seed URL siap dirayapi.")
            
            # Eksekusi Deep Crawl secara masif pada hasil pencarian (Kedalaman 1)
            for target_url in urls:
                AutonomousBrowser.start_crawl_job(target_url, depth=1)
                
            log.info(f"[Browser] Selesai menyerap kluster pengetahuan untuk topik '{search_query}'.")
            return urls
            
        except Exception as e:
            log.error(f"[Browser] Kegagalan eksplorasi publik: {e}")
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
