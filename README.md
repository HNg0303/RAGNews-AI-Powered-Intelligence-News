# RAGNews: Agentic AI-Powered Intelligent News Platform

A production-grade, stateful Retrieval-Augmented Generation (RAG) platform that intelligently aggregates, processes, and provides conversational access to global news. Built with an Agentic RAG architecture, RAGNews features an asynchronous ingestion pipeline, robust state management, and database-aware AI tools to deliver highly personalized and contextually accurate insights.

## 🎯 Project Overview

RAGNews bridges the gap between raw, multi-source news streams and actionable intelligence. Moving beyond standard semantic search, the system utilizes an AI Agent equipped with specific tools (Retrieval, Database Operations, and Summarization) to dynamically route queries and synthesize information. The backend is powered by a robust asynchronous ingestion pipeline that seamlessly routes text to PostgreSQL and Milvus, while handling media via Cloudinary.

**Live Demo:** [https://ragnews.streamlit.app](https://ragnews.streamlit.app)

## ✨ Key Features

* **Automatic Data Ingestion Pipeline:** A high-performance asynchronous web scraper that extracts articles and media, automatically routing structured metadata to **PostgreSQL**, generating and storing embeddings in **Milvus**, and offloading media assets to **Cloudinary**.
* **Agentic RAG Service:** A sophisticated RAG Agent that reasons through user queries using Database-Aware Tools:
    * *Retriever Tool:* Performs hybrid semantic search and reranking on the Milvus vector store.
    * *Database Ops Tool:* Queries PostgreSQL for exact metadata, dates, authors, and source filtering.
    * *Summarization Tool:* Generates concise, LLM-driven overviews of complex topics or specific articles.
* **State Management & Personalization:** Full session persistence with dedicated Thread and Message management. The system maintains conversational context across each unique chat, enabling personalized follow-ups and deep-dive analysis.
* **Dual-Interface Deployment:** A scalable FastAPI backend for programmatic interactions and a polished, responsive Streamlit dashboard for end-users.

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           User Interface Layer                          │
│        ┌────────────────────────┐         ┌────────────────────────┐    │
│        │ Streamlit UI (Cloud)   │◄───────►│ FastAPI REST Endpoints │    │
│        └────────────────────────┘         └────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
┌─────────────────────────────────────────────────────────────────────────┐
│                          Agentic RAG Layer                              │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ RAG Agent Orchestrator (LangGraph / LangChain)                    │  │
│  │ ├─ State & Thread Management (Message History)                    │  │
│  │ ├─ Context Formatting & Prompt Engineering                        │  │
│  │ └─ Tool Routing                                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│        │                           │                           │        │
│ ┌──────────────┐            ┌──────────────┐            ┌──────────────┐│
│ │ Retriever    │            │ Database Ops │            │ Summarizer   ││
│ │ Tool         │            │ Tool         │            │ Tool         ││
│ └──────┬───────┘            └──────┬───────┘            └──────┬───────┘│
└────────┼───────────────────────────┼───────────────────────────┼────────┘
         │                           │                           │
┌────────▼───────────────────────────▼───────────────────────────▼────────┐
│                             Storage Layer                               │
│  ┌────────────────────┐   ┌────────────────────┐   ┌─────────────────┐  │
│  │ Milvus (Zilliz)    │   │ PostgreSQL         │   │ Cloudinary      │  │
│  │ - Embeddings       │   │ - Threads/Messages │   │ - Article Images│  │
│  │ - Semantic Search  │   │ - Article Metadata │   │ - CDN Delivery  │  │
│  └─────────▲──────────┘   └─────────▲──────────┘   └───────▲─────────┘  │
└────────────┼────────────────────────┼──────────────────────┼────────────┘
             │                        │                      │
┌────────────┴────────────────────────┴──────────────────────┴────────────┐
│                       Async Data Ingestion Pipeline                     │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ Async Web Scraper & Processor                                     │  │
│  │ - Text Chunking & Embedder Integration                            │  │
│  │ - Metadata Extraction                                             │  │
│  │ - Image Download & Cloud Upload                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🛠️ Models & Tech Stack

**Databases & Storage:**
* **PostgreSQL:** Primary relational database for article metadata, user state, thread tracking, and message history.
* **Milvus (Zilliz Cloud):** High-performance vector database for storing document chunks and executing semantic similarity searches.
* **Cloudinary:** Cloud-based image management and CDN for storing scraped article thumbnails and media.

**AI & Machine Learning Models:**
* **Generative Engine:** Google Gemini (e.g., `gemini-1.5-pro`) serving as the core reasoning engine for the RAG Agent and summarization tasks.
* **Embedder:** `BAAI/bge-base-en-v1.5` for generating high-quality vector representations of text.
* **Reranker:** `BAAI/bge-reranker-base` (or Cohere) to refine and re-order retrieved contexts before passing them to the LLM.

**Backend & Frameworks:**
* **Python:** FastAPI, LangChain/LangGraph, SQLAlchemy, BeautifulSoup4, Asyncio.
* **Frontend:** Streamlit.

## 📦 Installation & Configuration

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/RAGNews.git
cd RAGNews
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables (`.env`)
Create a `.env` file in the root directory. You will need API keys and connection strings for the updated stack:

```env
# Server
PROJECT_NAME="RAGNews Intelligence Platform"
HOST="0.0.0.0"
PORT=8000

# PostgreSQL Database
DATABASE_URL="postgresql://user:password@localhost:5432/ragnews"

# Vector Database (Milvus/Zilliz)
ZILLIZ_URI="https://your-cluster.zilliz.cloud"
ZILLIZ_API_KEY="your_zilliz_key"

# Cloudinary (Image Hosting)
CLOUDINARY_CLOUD_NAME="your_cloud_name"
CLOUDINARY_API_KEY="your_api_key"
CLOUDINARY_API_SECRET="your_api_secret"

# LLMs & Embeddings
GOOGLE_API_KEY="your_gemini_key"
COHERE_API_KEY="your_cohere_key" # Optional for reranking
EMBEDDING_MODEL="BAAI/bge-base-en-v1.5"
CHAT_MODEL="gemini-1.5-pro"
```

## 🚀 Usage

### 1. Running the FastAPI Backend
The backend manages the async ingestion, database connections, and the Agentic RAG endpoints.
```bash
# Apply database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Streamlit Deployment
The frontend is hosted and automatically deployed via Streamlit Community Cloud. 
* **Live App:** [https://ragnews.streamlit.com](https://ragnews.streamlit.com)
* *Local Testing:* To run the frontend locally and connect it to your local backend:
    ```bash
    streamlit run app.py
    ```

### 3. Triggering the Ingestion Pipeline
You can trigger the async web scraper programmatically or via the backend API to ingest new data:
```python
import asyncio
from scraper.pipeline import run_ingestion

# Asynchronously scrape, embed, and upload images
asyncio.run(run_ingestion())
```

## 🔮 Future Roadmap

* [ ] **Unsupervised Trend Clustering:** Implement background ML pipelines (e.g., HDBSCAN/K-Means on Milvus vectors) to automatically detect, group, and label emerging news narratives and micro-trends across different sources over time.
* [ ] **Multi-Agent Collaboration:** Split the RAG Agent into specialized sub-agents (e.g., Financial Analyst Agent, Political Fact-Checker).
* [ ] **Real-Time WebSocket Streaming:** Stream LLM reasoning steps and chunks directly to the UI.
* [ ] **Advanced User Analytics:** Track query patterns to pre-cache personalized news digests. 