Intelligent Web Crawler with Embeddings & Elasticsearch Indexing

**Enterprise-Grade Recursive Web Scraper + Embedding Pipeline + Elasticsearch Storage**

A scalable web crawling system that recursively extracts website content, generates vector embeddings, and stores structured documents in **Elasticsearch** for semantic search and AI-powered retrieval use cases.


## Project Overview

This system:

* Recursively crawls web pages (configurable depth)
* Cleans and structures extracted HTML content
* Chunks large content intelligently
* Generates secure bearer token for embedding service
* Converts text into vector embeddings
* Stores content + embeddings in Elasticsearch
* Avoids duplicate URL processing
* Maintains logging & URL processing counts

Designed for **Enterprise RAG pipelines, Knowledge Indexing, and Semantic Search systems.**


## Architecture Flow

```
Seed URL
   ↓
Recursive Web Crawling
   ↓
HTML Cleaning (Remove Script/Style)
   ↓
Content Chunking
   ↓
Embedding Generation (API)
   ↓
Elasticsearch Index Storage
   ↓
Semantic Search Ready
```

## Key Capabilities

### Recursive Crawling

* Depth-controlled crawling (default depth = 2)
* Tracks visited URLs to prevent duplication
* Filters unwanted links (PDF, Images, mailto, fragments)

### Intelligent Content Processing

* Removes script & style elements
* Cleans whitespace
* Word-based chunking (default: 1000 words)

### Embedding Pipeline

* Secure token-based authentication
* External embedding API integration
* Vector generation for semantic indexing

### Elasticsearch Integration

* Multi-node connection support
* Stores:

  * URL
  * Cleaned content
  * Embedded vector
* Uses URL as document ID (avoids duplicates)

### Enterprise Logging

* Structured logging to `MetaData2.log`
* Error tracking
* URL processing count

## Tech Stack

* **Python 3.x**
* `requests`
* `BeautifulSoup (bs4)`
* `Elasticsearch`
* `urllib3`
* Environment-based configuration
* Vector Embedding API
* Recursive Web Crawling

## Secure Configuration

All sensitive configurations are managed using **environment variables**:

| Variable        | Description               |
| --------------- | ------------------------- |
| `PROXY_ADDRESS` | Proxy server              |
| `TOKEN_URL`     | Token generation endpoint |
| `APP_ID`        | Application ID            |
| `EMBED_URL`     | Embedding API endpoint    |
| `ES_USERNAME`   | Elasticsearch username    |
| `ES_PASSWORD`   | Elasticsearch password    |

This ensures secure deployment without hardcoding credentials.


## Installation

```bash
pip install requests
pip install beautifulsoup4
pip install elasticsearch
pip install urllib3
```

## ▶️ How to Run

1️⃣ Set environment variables

2️⃣ Add your seed URLs:

```python
urls_list = ["https://example.com"]
```

3️⃣ Run:

```bash
python main.py
```

## Stored Document Structure (Elasticsearch)

```json
{
  "url": "https://example.com/page",
  "url_content": "Cleaned chunked text...",
  "url_embedded_data": [0.0123, -0.9834, 0.4456, ...]
}
```

## 🎯 Use Cases

* Enterprise Knowledge Base Indexing
* Retrieval-Augmented Generation (RAG)
* Internal Documentation Search
* Semantic Search Systems
* Financial / Legal Content Archiving
* Corporate Website Intelligence



## Author

**Neha V Annam**
AI & Data Engineer


