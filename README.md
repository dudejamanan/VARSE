# VARSE: Video Analysis & Retrieval Semantic Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/Framework-LangChain-red)](https://python.langchain.com/)

**VARSE** is an intelligent learning ecosystem that transforms multiple YouTube videos into a unified, structured, and queryable knowledge base. 

Instead of relying on a single source, VARSE ingests multiple videos on a topic, extracts semantic meaning, and builds a "knowledge layer." It acts as a personalized AI tutor that not only answers queries but also evaluates which video explains a concept best based on clarity, depth, and your specific needs.

---

## 🚀 Features

### 📥 Intelligent Ingestion & Processing
* **Multi-Video Support:** Batch process multiple YouTube URLs.
* **Context-Aware Chunking:** Smart transcript splitting with overlapping windows to preserve semantic continuity.
* **Metadata Tagging:** Source-aware indexing using `video_id` for precise citation.

### 🧠 Advanced Analysis
* **LLM Grading:** Automated extraction of topics, subtopics, and teaching quality (Clarity/Structure).
* **Difficulty Profiling:** Categorizes content into **Beginner**, **Intermediate**, or **Advanced** levels.
* **Comparison Engine:** Dynamically identifies the best source for specific concepts.

### 🔍 Search & Generation
* **Semantic Retrieval:** Uses FAISS and HuggingFace embeddings for high-accuracy RAG (Retrieval-Augmented Generation).
* **Comparative Synthesis:** Generates answers that cross-reference multiple sources and explain *why* one source might be better than another.

---

## 🏗️ Architecture

```mermaid
graph TD
    A[YouTube URLs] --> B[Transcript Extraction]
    B --> C[Chunking & Metadata Tagging]
    C --> D[LLM Analysis: Topics, Clarity, Depth]
    D --> E[Embeddings Generator]
    E --> F[(FAISS Vector Store)]
    
    G[User Query] --> H[Semantic Retrieval]
    F --> H
    H --> I[Source-Grouped Context]
    I --> J[Comparative Answer Generation]
    J --> K[Final Response & Recommendations]
