# 🚀 OpenFetcher

**OpenFetcher** is a high-performance, LLM-native crawling engine that transforms entire domains into high-fidelity, semantic Markdown with embedded visual context. Engineered for the RAG era, it delivers lightning-fast, structured data streams optimized for agentic workflows and massive-scale knowledge ingestion.

![OpenFetcher Demo](./Screen-Recording-ezgif.com-optimize.gif) 

---

## ✨ Features

* **Deep Semantic Crawling**: Recursively discovers and maps entire domain structures using intelligent sitemap parsing.
* **LLM-Ready Markdown**: Converts complex HTML into clean, structured Markdown optimized for RAG context windows.
* **Visual Context Preservation**: Captures high-fidelity images and maintains their semantic relationship with the surrounding text.
* **Real-Time Telemetry**: Provides per-page execution timing and live streaming NDJSON output.
* **Parallel Architecture**: Orchestrates concurrent headless browsers for rapid, large-scale extraction.

---

## 🏗️ Architecture

```mermaid
graph TD
    A[Start URL] --> B[OpenFetcher Engine]
    B --> C{Discovery Phase}
    C -->|Sitemaps| D[https://en.wikipedia.org/wiki/Queue_%28abstract_data_type%29](https://en.wikipedia.org/wiki/Queue_%28abstract_data_type%29)
    C -->|Link Extraction| D
    D --> E[Parallel Worker Pool]
    E -->|Selenium Headless| F[Content Extraction]
    F -->|Markdownify| G[LLM-Ready Markdown]
    G --> H[Streaming Response / Webhook]
🚀 Getting Started1. PrerequisitesPython 3.10+Google Chrome / Chromedriver[Recommended] 8GB+ RAM for high-concurrency local runs.2. Local InstallationBash# Clone the repository
git clone [https://github.com/PremChaurasiya07/OpenFetcher.git](https://github.com/PremChaurasiya07/OpenFetcher.git)
cd OpenFetcher

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
3. Run LocallyBashuvicorn main:app --host 0.0.0.0 --port 3003
⚙️ Increasing Limits (Local Power User)When running on your local machine (instead of Render's free tier), you can significantly increase the engine's speed and capacity.Edit the following constants in scraper_engine.py:ConstantRender LimitLocal RecommendationResultMAX_CONCURRENT_BROWSERS15 - 1010x faster scraping speed.PAGE_LIMIT15100 - 500Deep-domain crawling.time.sleep()2.0s0.5s - 1.0sFaster page transitions.Pro Tip: For local runs, ensure your MAX_CONCURRENT_BROWSERS does not exceed your CPU core count to prevent system lag.📡 API UsageEndpoint: POST /scrapePayload:JSON{
  "url": "[https://supermemory.ai](https://supermemory.ai)",
  "site_id": "unique_identifier"
}
📄 LicenseDistributed under the MIT License. See LICENSE for more information.
---

### **Final Instructions for You**

1.  **Create the File**: Create a new file named `README.md` in your `scraper-engine` folder.
2.  **Paste the Content**: Paste the code block above into that file.
3.  **Local Boost**: In your `scraper_engine.py`, change `MAX_CONCURRENT_BROWSERS = 5` and `PAGE_LIMIT = 100` now that you aren't limited by Render's 512MB RAM.
4.  **Final Push**:
    ```bash
    git add README.md scraper_engine.py
    git commit -m "Docs: Add professional README and increase local limits"
    git push origin main
    ```