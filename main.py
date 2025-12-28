import json
import logging
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import StreamingResponse
from scraper_engine import scrape_full_site_generator
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("ScraperEngine")

app = FastAPI(title="OpenBot Ultra Scraper")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, replace "*" with your specific backend/frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scrape")
async def scrape_endpoint(
    url: str = Body(..., embed=True),
    site_id: str = Body(..., embed=True)
):
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    async def event_generator():
        # Pass site_id to the generator so it can be used for webhooks
        async for page_data in scrape_full_site_generator(url, site_id):
            logger.info(f"📤 Streaming: {page_data['url']}")
            yield json.dumps(page_data) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

@app.get("/health")
def health():
    return {"status": "ready"}