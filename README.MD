<div align="center">

# 🔧 FixFlow

### *The Autonomous Error Intelligence & Automated Diagnostic RAG Platform*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICIENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20Store-red.svg)](https://qdrant.tech/)
[![Docker](https://img.shields.io/badge/Docker-Containers-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

**Paste any software error or stack trace → FixFlow classifies the issue, performs semantic vector retrieval across developer sources, and generates evidence-grounded solutions with actionable code patches.**

[Quick Start](#-quick-start-3-simple-steps) • [How It Works](#-how-to-use-fixflow) • [Docker Services](#-docker-infrastructure-services) • [API Reference](#-api-endpoints) • [Troubleshooting](#-troubleshooting--faq)

</div>

---

## 📖 What is FixFlow?

FixFlow is an intelligent error resolution system built with **Python**, **FastAPI**, and **Vector RAG (Retrieval-Augmented Generation)**.

Instead of manually browsing Stack Overflow and GitHub issues for hours, FixFlow:
1. **Parses & Sanitizes**: Normalizes raw tracebacks, extracting error signatures, language tags, and error types.
2. **Clusters & Categorizes**: Groups similar errors automatically into semantic clusters using dense text embeddings.
3. **Semantic Retrieval**: Queries high-dimensional vector stores (Qdrant) and developer forums for real matching solutions.
4. **Diagnostic Generation**: Produces a root-cause explanation, verified step-by-step fix, and copy-pasteable code patches.
5. **Adaptive Feedback Loop**: Automatically invalidates poor answers and regenerates improved solutions based on user ratings.

```
┌──────────────────┐      ┌─────────────────────────┐      ┌───────────────────────────┐
│ Paste Any Error  │ ───► │ Semantic Vector Search  │ ───► │ Root Cause + Code Patch   │
│ (Raw Traceback)  │      │ (Qdrant + GitHub/SO)    │      │ (Grounded Diagnostic Fix) │
└──────────────────┘      └─────────────────────────┘      └───────────────────────────┘
```

---

## 🚀 Quick Start (3 Simple Steps)

You only need **Python 3.10 or higher** installed on your machine.

### 1. Clone the repository
Open your terminal (macOS/Linux) or Command Prompt / PowerShell (Windows):
```bash
git clone https://github.com/kerlosmelad12/FixFlow-.git
cd FixFlow-
```

### 2. Create and activate a virtual environment
```bash
# Create the virtual environment
python3 -m venv venv

# Activate it:
# On macOS / Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install requirements & run
```bash
# Install Python packages
pip install -r src/requirements.txt

# Start the FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 5000
```

🎉 **You're up and running!**
- **Interactive Swagger API Docs**: 👉 [http://localhost:5000/docs](http://localhost:5000/docs)
- **Interactive Redoc**: 👉 [http://localhost:5000/redoc](http://localhost:5000/redoc)
- **Web Interface**: Open `src/frontend/index.html` directly in your browser or navigate through the static server.

---

## 🐳 Docker Infrastructure Services (Optional)

FixFlow integrates with **Qdrant**, **Redis**, and **MongoDB** for production-grade vector search and caching. You can start all of them with a single command:

```bash
cd docker
docker compose up -d
```

| Service | Port | Purpose |
|---|---|---|
| **Qdrant** | `6333` | High-dimensional vector database for semantic similarity matching |
| **Redis** | `6379` | High-speed cache for error deduplication and job statuses |
| **MongoDB** | `27017` | Persistent storage for error documents, answers, and feedback |

---

## 🖥️ How to Use FixFlow

### 1. Upload an Error
Send your stack trace or error message via the frontend or API:
```bash
curl -X POST http://localhost:5000/Fixflow-V1/data/upload/ \
  -H "Content-Type: application/json" \
  -d '{"query": "TypeError: Cannot read properties of undefined (reading '\''map'\'') at App.jsx:42"}'
```
*Response returns a unique `error_id`, deterministic hash, and assigned error cluster.*

### 2. Generate a Solution
Request a structured diagnosis:
```bash
curl -X POST http://localhost:5000/Fixflow-V1/nlp/answer/<YOUR_ERROR_ID>
```
*Response delivers:*
- **Root Cause**: What broke and why.
- **Steps**: Ordered resolution procedure.
- **Code Fix**: Defensive, corrected code snippet.
- **Sources**: Real matching discussions from developer forums.

### 3. Submit Feedback
Rate the accuracy of the answer from 1 to 5:
```bash
curl -X POST http://localhost:5000/Fixflow-V1/nlp/answer/<YOUR_ERROR_ID>/feedback \
  -H "Content-Type: application/json" \
  -d '{"feedback_text": "Worked perfectly, thank you!", "score": 5}'
```
*If a low rating is submitted (score < 3), FixFlow automatically triggers context regeneration.*

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and fill in your credentials if using cloud LLM providers:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `LLM_PROVIDER` | Model provider (`groq`, `qwen`, or `sentence`) |
| `LLM_API_KEY` | API key for external LLM inference |
| `REDIS_URL` | Redis connection URL (`redis://localhost:6379`) |
| `MONGODB_URI` | MongoDB connection URI (`mongodb://localhost:27017`) |
| `VECTOR_STORE_BACKEND` | Vector store provider (`qdrant`) |
| `EMBEDDING_MODEL_NAME` | Embedding model for semantic search (e.g., `all-MiniLM-L6-v2`) |

---

## 🔌 API Endpoints

All endpoints are versioned under the `/Fixflow-V1` prefix:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/Fixflow-V1/` | Service health check and version metadata |
| `POST` | `/Fixflow-V1/data/upload/` | Submit new error; performs extraction & clustering |
| `GET` | `/Fixflow-V1/data/search/{error_id}` | Retrieve processing job status for an error |
| `DELETE` | `/Fixflow-V1/data/error/{error_id}` | Remove error record, job, and cached answers |
| `POST` | `/Fixflow-V1/nlp/similar/{error_id}` | Semantic similarity retrieval across web & vector sources |
| `POST` | `/Fixflow-V1/nlp/answer/{error_id}` | Generate/retrieve RAG diagnostic solution and code fix |
| `POST` | `/Fixflow-V1/nlp/answer/{error_id}/feedback` | Record user feedback with sentiment analysis |

---

## 📁 Repository Structure

```
FixFlow/
├── docker/                      # Container infrastructure
│   └── docker-compose.yaml      # Qdrant, MongoDB, and Redis definitions
├── notebooks/                   # R&D, experimentation, and model tuning
│   ├── Classification.ipynb     # Error classification & clustering models
│   ├── Cluster_naming.ipynb     # Automated cluster naming pipeline
│   ├── Data Scrape.ipynb        # Scraping and dataset curation
│   └── embedding.ipynb          # Sentence embedding evaluations
├── src/
│   ├── controllers/             # Core business logic & orchestrators
│   ├── models/                  # Database schemas, Pydantic models, & enums
│   ├── routes/                  # FastAPI routers (data & NLP endpoints)
│   ├── stores/                  # Vector DB, Redis cache, & LLM providers
│   ├── frontend/                # Interactive web client (HTML/CSS/JS)
│   ├── main.py                  # FastAPI application entry point
│   └── requirements.txt         # Python project dependencies
├── .env.example                 # Environment configuration template
├── README.md                    # Project documentation
└── LICIENSE                     # License information
```

---

## ❓ Troubleshooting & FAQ

<details>
<summary><b>Q: "command not found: python3" or "python is not recognized"</b></summary>
<br/>
Ensure Python 3.10+ is installed from <a href="https://www.python.org/downloads/">python.org</a>. On Windows, make sure to check the box <b>"Add Python to PATH"</b> during installation.
</details>

<details>
<summary><b>Q: Can I run without Docker?</b></summary>
<br/>
Yes! Docker is only required if you want local instances of MongoDB, Redis, and Qdrant. For quick testing, you can use remote/cloud instances or configure in-memory backends.
</details>

<details>
<summary><b>Q: How do I test the API interactively?</b></summary>
<br/>
Once running, visit <code>http://localhost:5000/docs</code>. FastAPI provides an interactive Swagger UI where you can try every endpoint directly from your browser.
</details>

---

## 👨‍💻 Author

**Kerlos Melad**  
- GitHub: [@kerlosmelad12](https://github.com/kerlosmelad12)  
- Email: kerlosmelad124@gmail.com  

---

## 📄 License

This project is licensed under the [MIT License](./LICIENSE).
