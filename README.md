# RAGNews: AI-Powered Intelligent News System

A comprehensive Retrieval-Augmented Generation (RAG) platform that intelligently aggregates, processes, and provides conversational access to news articles from multiple sources. Built with LangChain, Milvus vector database, and Google's generative AI models, RAGNews enables users to ask natural language questions about current news topics and receive contextually accurate, sourced responses.

## 🎯 Project Overview

RAGNews combines web scraping, vector embeddings, and advanced language models to create an intelligent news retrieval and generation system. The platform automatically collects news articles from major sources, stores them in a high-performance vector database, and provides both REST API and web-based interfaces for querying and analysis.

### Key Features

- **Multi-Source News Aggregation**: Automated scraping from CNN, AP News, and Financial Press
- **Vector Search**: Fast, semantic similarity search using embeddings and Milvus vector database
- **RAG Architecture**: Combines retrieved documents with generative AI for accurate, sourced responses
- **Web Scraping Pipeline**: Intelligent extraction of articles, images, and metadata
- **Dual Interface**: FastAPI backend for programmatic access and Streamlit dashboard for interactive use
- **Image Handling**: Automatic downloading and organization of article images
- **Scalable Vector Database**: Milvus-powered embeddings with semantic search capabilities
- **Production-Ready**: Built with security, configuration management, and error handling

## 📋 Table of Contents

- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Components](#components)
- [License](#license)

## 🏗️ Architecture

RAGNews follows a modular, layered architecture:

```
┌─────────────────────────────────────────────────────┐
│          User Interface Layer                        │
│  ┌──────────────────┐      ┌──────────────────┐    │
│  │  Streamlit UI    │      │  FastAPI REST    │    │
│  │  (Dashboard)     │      │  (API Endpoints) │    │
│  └──────────────────┘      └──────────────────┘    │
└─────────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────────┐
│          RAG Engine Layer                            │
│  ┌────────────────────────────────────────────┐    │
│  │  RAG Chain: Retriever + Generator          │    │
│  │  - Prompt Templates                        │    │
│  │  - Context Formatting                      │    │
│  │  - LLM Integration                         │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────────┐
│          Processing Layer                           │
│  ┌──────────────────┐      ┌──────────────────┐    │
│  │  Retriever       │      │  Text Splitter   │    │
│  │  (Semantic       │      │  (Chunking)      │    │
│  │   Search)        │      │                  │    │
│  └──────────────────┘      └──────────────────┘    │
│  ┌──────────────────┐      ┌──────────────────┐    │
│  │  Embedder        │      │  Reranker        │    │
│  │  (BGE Models)    │      │  (Ranking)       │    │
│  └──────────────────┘      └──────────────────┘    │
└─────────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────────┐
│          Storage Layer                              │
│  ┌────────────────────────────────────────────┐    │
│  │  Milvus Vector Database (Zilliz)          │    │
│  │  - Embeddings Storage                      │    │
│  │  - Metadata Indexing                       │    │
│  │  - Fast Similarity Search                  │    │
│  └────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────┐    │
│  │  Local File Storage                        │    │
│  │  - JSON Articles                           │    │
│  │  - Downloaded Images                       │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────────┐
│          Data Collection Layer                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Web Scraper                                │  │
│  │  - CNN Article Extraction                   │  │
│  │  - AP News Article Extraction               │  │
│  │  - Financial Press Article Extraction       │  │
│  │  - Image Download Pipeline                  │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Data Flow**:
1. **Collection**: Scraper fetches articles from multiple news sources
2. **Storage**: Articles stored locally as JSON with downloaded images
3. **Indexing**: Documents split into chunks and converted to embeddings
4. **Retrieval**: User queries matched against stored embeddings
5. **Generation**: Retrieved context combined with user question for LLM
6. **Response**: Sourced AI-generated response delivered to user

## 📁 Project Structure

```
RAGNews/
├── core/                          # Core configuration and security
│   ├── config.py                 # Settings management (using Pydantic)
│   ├── security.py               # Authentication and security utilities
│   └── __init__.py
│
├── scraper/                       # Web scraping module
│   ├── scrape.py                 # Main scraping orchestration
│   │   ├── get_cnn_articles()
│   │   ├── extract_cnn_articles()
│   │   ├── get_apnews_articles()
│   │   ├── extract_apnews_articles()
│   │   └── get_fp_articles()
│   ├── utils.py                  # Helper functions (image download, parsing)
│   └── __init__.py
│
├── src/                           # Core application source code
│   ├── api/                       # REST API layer
│   │   ├── router.py             # FastAPI route definitions
│   │   ├── scraper/              # API-specific scraper endpoints
│   │   └── __init__.py
│   │
│   ├── database/                  # Vector database and storage
│   │   ├── embedder.py           # Embedding models (BGE, Sentence Transformers)
│   │   ├── vector_store.py       # Milvus/Zilliz integration
│   │   └── __init__.py
│   │
│   ├── engine/                    # RAG pipeline engine
│   │   ├── engine.py             # Main RAG chain orchestration
│   │   ├── retriever.py          # Document retrieval with reranking
│   │   ├── generation.py         # LLM generation with Google GenAI
│   │   ├── indexing.py           # Document indexing pipeline
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── data/                          # Data storage directory
│   ├── raw_news/                 # Raw HTML/JSON articles
│   ├── finance/                  # Financial news articles
│   │   ├── fp.json              # Parsed articles
│   │   └── fp.html              # Raw HTML pages
│   ├── general/                  # General news (CNN, AP News)
│   │   ├── apnews.json
│   │   ├── cnn.json
│   │   └── *.html
│   └── images/                   # Downloaded article images
│       └── [article_id]/         # Images grouped by article
│
├── docs/                          # Documentation
├── notebooks/                     # Jupyter notebooks for experimentation
│
├── main.py                        # FastAPI application entry point
├── requirements.txt               # Python dependencies
├── config.env                     # Environment configuration (not in repo)
├── LICENSE                        # License information
└── README.md                      # This file
```

## 🔧 Prerequisites

- **Python**: 3.9 or higher
- **System Requirements**:
  - 4GB RAM minimum (8GB recommended)
  - 10GB disk space for articles and images
  - Internet connection for scraping and API calls
- **External Services**:
  - Milvus/Zilliz Cloud account for vector database
  - Google Cloud API key for Gemini models
  - Cohere API key (optional, for enhanced reranking)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/RAGNews.git
cd RAGNews
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n ragnews python=3.11
conda activate ragnews
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# FastAPI Configuration
PROJECT_NAME="My Daily RAG Newspaper"
HOST="localhost:8000"

# Vector Database (Milvus/Zilliz Cloud)
ZILLIZ_URI="https://your-cluster.zilliz.cloud"
ZILLIZ_API_KEY="your_api_key_here"

# LLM Configuration
GOOGLE_API_KEY="your_google_api_key_here"
COHERE_API_KEY="your_cohere_api_key_here"  # Optional

# Embedding Models
EMBEDDING_MODEL="BAAI/bge-base-en-v1.5"
RERANKING_MODEL="BAAI/bge-reranker-base"
CHAT_MODEL="gemini-1.5-pro"

# Scraping Configuration
SCRAPE_TIMEOUT=10
MAX_RETRIES=3
```

## ⚙️ Configuration

### Core Settings (`core/config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "My Daily RAG Newspaper"
    host: str = "localhost:8000"
    # Additional settings loaded from .env
```

Load settings in your application:

```python
from core.config import setting
print(setting.project_name)
```

## 🚀 Usage

### Running the Streamlit Dashboard

The project includes a Streamlit application with a polished UI (`app_1.py` in the repository; you may rename it to `app.py` if preferred) that provides an interactive interface with three pages:

1. **Headlines (Home)** – Displays a grid of randomly selected articles from `data/raw_news`. Each card shows the article image (if available) with the headline overlaid. Click "Read more" to view the full article.
2. **Article Detail** – Shows the title, main image, and full content of the selected article. A "Back to headlines" button returns you to the home page.
3. **News Chatbot** – Chat interface powered by the RAG pipeline (`RAGChain`). Enter a natural language question about the news and receive a response with cited sources. Conversations are preserved during the session.

To start the dashboard:

```bash
streamlit run app.py
```

The UI automatically scans `data/raw_news` recursively and will display any JSON articles you have scraped. Sample/demo articles are only used if no real data is found. Ensure you have populated `data/raw_news` (e.g. by running the scraper) and set up your `.env` with the required keys before using the chatbot.


### Web Scraping

```python
from scraper.scrape import get_cnn_articles, extract_cnn_articles
import requests
from bs4 import BeautifulSoup

# Fetch and parse CNN articles
response = requests.get("https://www.cnn.com")
soup = BeautifulSoup(response.content, 'html.parser')

# Get article links
articles = get_cnn_articles(soup, url="https://www.cnn.com")

# Extract article details
for article in articles:
    article_soup = BeautifulSoup(
        requests.get(article['article_link']).content,
        'html.parser'
    )
    details = extract_cnn_articles(article_soup, article['id'])
```

### RAG Query Example

```python
from src.engine.engine import RAGChain
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize RAG Chain
rag = RAGChain(
    embedding_model="BAAI/bge-base-en-v1.5",
    reranking_model="BAAI/bge-reranker-base",
    chat_model="gemini-1.5-pro",
    cloud_uri=os.getenv("ZILLIZ_URI"),
    cloud_api_key=os.getenv("ZILLIZ_API_KEY"),
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Query the RAG system
response = rag.query("What are the latest developments in technology?")
print(response)
```
## 🧠 Components

### Scraper Module (`scraper/`)

Handles news article collection from multiple sources with intelligent parsing and image downloading.

**Features**:
- BeautifulSoup-based HTML parsing
- Multi-source support (CNN, AP News, Financial Press)
- Automatic image downloading and organization
- Error handling and logging
- Article metadata extraction

### Database Module (`src/database/`)

**Embedder** (`embedder.py`):
- Multi-model embedding support
- Default: BAAI/bge-base-en-v1.5 (384-dimensional vectors)
- Semantic similarity computation

**Vector Store** (`vector_store.py`):
- Milvus/Zilliz integration
- Document chunking and splitting
- Embedding storage and indexing
- Similarity search with metadata filtering

### Engine Module (`src/engine/`)

**RAG Chain** (`engine.py`):
- Orchestrates retrieval and generation
- Prompt template management
- Context formatting
- LangChain runnable chains

**Retriever** (`retriever.py`):
- Semantic search with embeddings
- Re-ranking for result quality
- Metadata filtering
- Top-K result retrieval

**Generation** (`generation.py`):
- Google Gemini integration
- Prompt engineering
- Response formatting
- Source citation

**Indexing** (`indexing.py`):
- Document processing pipeline
- Metadata extraction
- Batch indexing
- Update and deletion support

## 📄 License

This project is licensed under the LICENSE file in the repository. See [LICENSE](LICENSE) for details.

## 🔮 Future Roadmap

- [ ] Real-time article updating
- [ ] Multi-language support
- [ ] Advanced filtering and search
- [ ] User authentication and personalization
- [ ] Caching layer for performance
- [ ] WebSocket support for live updates
- [ ] Mobile application
- [ ] Analytics and insights dashboard

## 📚 References

- [LangChain Documentation](https://python.langchain.com/)
- [Milvus Vector Database](https://milvus.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [Google Generative AI](https://ai.google.dev/)

---

**Last Updated**: March 2026
**Version**: 1.0.0