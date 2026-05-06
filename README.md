# Digesto GPT 🤖⚖️

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.0-38B2AC.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Digesto GPT** is an advanced AI-powered legal assistant and search engine specifically designed for the **Nicaraguan Juridical Digest** (*Digesto Jurídico Nicaragüense*). Leveraging state-of-the-art Retrieval-Augmented Generation (RAG) technology, it provides legal professionals and citizens with grounded, cited, and accurate answers to complex legal inquiries about Nicaraguan legislation.

---

## 🌟 Key Features

### 🔍 Advanced RAG Engine
- **Hybrid Search:** Combines semantic (dense) search with keyword-based (sparse BM25) search for maximum retrieval precision.
- **Statistical Chunking:** Utilizes advanced semantic chunking to preserve legal context across document fragments.
- **RRF Reranking:** Implements Reciprocal Rank Fusion to merge and optimize results from multiple search strategies.

### 💬 Intelligent Chat Interface
- **Real-time Streaming:** Token-by-token response streaming via WebSockets for a smooth user experience.
- **Grounded Citations:** Every response includes direct links to the source laws and specific fragments used.
- **Auto-Title Generation:** Automatically summarizes conversation topics for easy navigation.

### 📊 Enterprise-Grade Evaluation
- **Ragas Integration:** Automated pipeline to measure **Faithfulness**, **Answer Relevancy**, **Context Precision**, and **Recall**.
- **Metrics Dashboard:** Visual tracking of LLM performance and response quality.

### 🛠️ Law Management System
- **Document Ingestion:** Automated processing of HTML/PDF legal documents.
- **Metadata Management:** Full control over law categories, ranks, and validity statuses.
- **Asynchronous Processing:** Background tasks for embedding and indexing large volumes of legislation.

---

## 🛠️ Tech Stack

- **Backend:** 
  - [Django](https://www.djangoproject.com/) (Main Web Framework)
  - [FastAPI](https://fastapi.tiangolo.com/) (AI & Embedding Microservice)
  - [Django Channels](https://channels.readthedocs.io/) (WebSockets)
  - [Celery](https://docs.celeryq.dev/) + [Redis](https://redis.io/) (Task Queue)
- **AI / Machine Learning:**
  - [LangChain](https://www.langchain.com/) (LLM Orchestration)
  - [Google Gemini 2.0](https://deepmind.google/technologies/gemini/) (Primary LLM)
  - [HuggingFace](https://huggingface.co/) (Embeddings)
  - [Milvus](https://milvus.io/) (Vector Database)
  - [Ragas](https://docs.ragas.io/) (Evaluation Framework)
- **Frontend:**
  - [HTMX](https://htmx.org/) (Dynamic UI without complex JS)
  - [Tailwind CSS](https://tailwindcss.com/) (Responsive Design)
  - [Django Components](https://github.com/EmilStenstrom/django-components) (Modular UI)
- **Database:**
  - [PostgreSQL](https://www.postgresql.org/) (Structured Data)
  - [Milvus](https://milvus.io/) (Vector Data)

---

## 🏗️ Architecture Overview

Digesto GPT follows a microservices-inspired architecture to separate the web concerns from the heavy AI processing:

1.  **Django Server:** Handles user authentication, law management, conversation history, and real-time WebSocket communication.
2.  **FastAPI Service:** Dedicated to RAG operations, including embedding generation, hybrid search, and LLM orchestration.
3.  **Milvus Vector DB:** High-performance storage and retrieval of legal text embeddings.
4.  **PostgreSQL:** Stores metadata for laws, user data, and chat history.

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Poetry (for local development)
- Google Gemini API Key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/digesto-gpt.git
    cd digesto-gpt
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    # Django Settings
    SECRET_KEY=your_secret_key
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1

    # Database
    POSTGRES_DB=digesto_db
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    DATABASE_URL=postgres://postgres:postgres@db:5432/digesto_db

    # AI & Milvus
    GEMINI_API_KEY=your_gemini_api_key
    MILVUS_DB_URI=http://milvus-standalone:19530
    EMBEDDINGS_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
    MODELS_CHACHE_DIR=./models_cache
    ```

3.  **Run with Docker:**
    ```bash
    docker-compose up --build
    ```

4.  **Initialize Database:**
    ```bash
    docker-compose exec django-server python manage.py migrate
    docker-compose exec django-server python manage.py createsuperuser
    ```

---

## 📖 Usage

### Processing Laws
1. Log in to the admin panel or the Law Management section.
2. Upload legal documents (HTML format preferred).
3. The system will automatically trigger the chunking and embedding process.

### Chatting with the Digest
1. Navigate to the Chat section.
2. Ask questions like: *"¿Cuáles son los requisitos para la creación de una sociedad anónima según la Ley de Sociedades?"*
3. The bot will respond with grounded information and citations.

### Evaluating Performance
- Use the Metrics section to view the Ragas evaluation scores for recent conversations.
- Run the evaluation suite manually via the FastAPI endpoint `/evaluate-rag`.

---

## 📈 Evaluation Metrics

The project uses **Ragas** to ensure high-quality legal advice:
- **Faithfulness:** Ensures the answer is derived strictly from the retrieved context.
- **Answer Relevancy:** Measures how well the answer addresses the user's query.
- **Context Precision:** Evaluates the quality of the retrieved document chunks.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Michael** - [Sjeffmichael](https://github.com/Sjeffmichael)
*Passionate about AI, LegalTech, and Full-Stack Development.*
