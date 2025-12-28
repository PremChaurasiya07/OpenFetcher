import time
import logging
import asyncio
import httpx  # Added for Webhook notifications
import os
from typing import AsyncGenerator
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from markdownify import markdownify as md
from usp.tree import sitemap_tree_for_homepage

logger = logging.getLogger("ScraperEngine")

# --- CONFIG ---
MAX_CONCURRENT_BROWSERS = 1  # Keep 1 for Render Free Tier
PAGE_LIMIT = 15
# The URL of your Main Backend endpoint that handles progress updates
BACKEND_WEBHOOK_URL = os.getenv("BACKEND_WEBHOOK_URL", "http://localhost:8000/ingest/progress")

async def notify_backend(payload: dict):
    """Sends a notification with a retry attempt if it fails."""
    async with httpx.AsyncClient() as client:
        for attempt in range(3): # Try up to 3 times
            try:
                response = await client.post(BACKEND_WEBHOOK_URL, json=payload, timeout=10.0)
                if response.status_code == 200:
                    return
            except Exception as e:
                if attempt == 2: logger.error(f"❌ Webhook permanently failed: {e}")
                await asyncio.sleep(1) # Wait a second before retrying

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def extract_smart_content(driver) -> str:
    driver.execute_script("""
        const noise = ['nav', 'footer', 'script', 'style', 'header', 'aside', '.cookie-banner', 'form', 'svg', 'iframe', 'noscript', 'button'];
        noise.forEach(s => document.querySelectorAll(s).forEach(el => el.remove()));
        document.querySelectorAll('img').forEach(img => {
            const alt = img.getAttribute('alt') || '';
            const src = img.getAttribute('src') || '';
            if (alt.length < 5 || !src.startsWith('http')) { img.remove(); }
        });
    """)
    raw_md = md(driver.page_source, heading_style="ATX", bullets="-")
    return "\n".join([line.strip() for line in raw_md.split('\n') if line.strip()])

# --- PARALLEL WORKER ---
async def scrape_task(url: str, site_id: str, semaphore: asyncio.Semaphore):
    async with semaphore:
        result = await asyncio.to_thread(_sync_worker, url)
        if result:
            # Trigger Webhook: Notify backend that a specific page is ready
            await notify_backend({
                "site_id": site_id,
                "status": "PAGE_COMPLETED",
                "data": result
            })
        return result

def _sync_worker(url: str):
    driver = get_driver()
    try:
        driver.get(url)
        time.sleep(1.5) # Optimized wait
        content = extract_smart_content(driver)
        return {"url": url, "type": "SUPPORTING_DATA", "markdown": content}
    except Exception as e:
        logger.error(f"❌ Error scraping {url}: {e}")
        return None
    finally:
        driver.quit()

# --- MAIN ENGINE ---
async def scrape_full_site_generator(start_url: str, site_id: str, MAX_CONCURRENT_BROWSERS: int = 1, PAGE_LIMIT = 5) -> AsyncGenerator[dict, None]:
    start_time = time.perf_counter()
    parsed_start = urlparse(start_url)
    base_domain = parsed_start.netloc
    base_url = f"{parsed_start.scheme}://{base_domain}"
    
    driver = get_driver()
    discovery_queue = set()
    processed_urls = {start_url, base_url}

    try:
        # PHASE 1: Main Page
        driver.get(base_url)
        time.sleep(4) 
        main_md = extract_smart_content(driver)
        main_data = {"url": base_url, "type": "MAIN_PAGE", "markdown": main_md}
        
        await notify_backend({"site_id": site_id, "status": "PAGE_COMPLETED", "data": main_data})
        yield main_data

        # PHASE 2: Faster Discovery
        # We try sitemap but don't hang if it's slow
        try:
            tree = sitemap_tree_for_homepage(base_url)
            for page in tree.all_pages():
                discovery_queue.add(page.url.rstrip('/'))
        except: pass

        links = driver.find_elements("tag name", "a")
        for link in links:
            href = link.get_attribute("href")
            if href and base_domain in href:
                discovery_queue.add(href.split('#')[0].rstrip('/'))
    finally:
        driver.quit()

    # PHASE 3: Parallel Batching
    remaining = list(discovery_queue - processed_urls)
    remaining.sort(key=lambda x: (urlparse(x).path.count('/'), len(x)))

    sem = asyncio.Semaphore(MAX_CONCURRENT_BROWSERS)
    tasks = [scrape_task(url, site_id, sem) for url in remaining[:PAGE_LIMIT]]

    for task in asyncio.as_completed(tasks):
        result = await task
        if result and len(result['markdown']) > 150:
            yield result

    total_time = round(time.perf_counter() - start_time, 2)
    await notify_backend({
        "site_id": site_id, 
        "status": "COMPLETED", 
        "total_time": total_time
    })
    logger.info(f"🏁 All tasks complete in {total_time}s")