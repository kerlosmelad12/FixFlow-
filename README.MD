<div align="center">

# 🔧 FixFlow

**AI-powered developer assistant for understanding, searching, and resolving software errors.**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Qdrant](https://img.shields.io/badge/Qdrant-vector%20search-DC244C)](https://qdrant.tech/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

</div>

---

## Overview

FixFlow turns a raw error message — a stack trace, a build failure, a runtime exception — into a **context-aware, evidence-backed solution**.

Instead of sending the raw query straight to an LLM and hoping for the best, FixFlow follows a **Retrieval-Augmented Generation (RAG)** pipeline: it understands the error with NLP, retrieves relevant technical knowledge from multiple sources (vector search, Stack Overflow, GitHub), ranks and filters that evidence, and only then generates a grounded answer — complete with sources and a confidence signal.

```
User → LLM → Answer                     (naive approach)

User → Understand → Retrieve → Process → LLM → Grounded Answer     (FixFlow)
```

---

## Table of Contents

- [Why FixFlow](#why-fixflow)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running with Docker](#running-with-docker)
- [Frontend Demo Client](#frontend-demo-client)
- [Example Walkthrough](#example-walkthrough)
- [Engineering Principles](#engineering-principles)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Author](#author)
- [License](#license)

---

## Why FixFlow

Developers routinely lose time debugging by manually:

- Searching Stack Overflow and GitHub issues
- Matching a new error against similar ones seen before
- Identifying the right framework/library context
- Comparing conflicting solutions
- Filtering out outdated or irrelevant results

Keyword search breaks down when a developer's phrasing doesn't match how the issue is described elsewhere. FixFlow addresses this with **semantic retrieval, NLP-based error understanding, multi-source search, and LLM-powered synthesis** — grounding every generated answer in retrieved evidence rather than the model's unaided memory.

---

## Key Features

| | |
|---|---|
| 🧠 NLP-based error understanding | Extracts error type, entities, and technical context from raw input |
| 🏷️ Technology / tag classification | Identifies the relevant frameworks and libraries involved |
| 🔎 Semantic vector search | Finds conceptually similar errors, not just keyword matches |
| 📚 Retrieval-Augmented Generation | Grounds LLM answers in retrieved technical evidence |
| 💬 Stack Overflow search | Pulls in real developer Q&A |
| 🐙 GitHub search | Pulls in real repository issues and fixes |
| 🤖 LLM-powered generation | Synthesizes retrieved evidence into one actionable answer |
| 🔗 Source tracing | Every answer keeps a link back to the evidence it came from |
| 🛡️ Confidence-aware processing | Guards against low-quality retrieval being surfaced as fact |
| ⚡ Redis caching | Avoids redundant search and generation calls |
| 🗄️ MongoDB persistence | Stores errors, jobs, answers, answer history, and feedback |
| 🐳 Docker-based infrastructure | One-command startup for MongoDB, Redis, and Qdrant |

---

## Architecture

```
                     ┌─────────────────────┐
                     │     User Query       │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │   NLP Processing     │
                     │ • Error extraction   │
                     │ • Entity extraction  │
                     │ • Tag prediction     │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │  Search Orchestrator │
                     └──────────┬───────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
   ┌─────────────┐      ┌─────────────┐       ┌─────────────┐
   │   Qdrant    │      │    Stack    │       │   GitHub    │
   │  Vector DB  │      │  Overflow   │       │   Search    │
   └──────┬──────┘      └──────┬──────┘       └──────┬──────┘
          │                    │                     │
          └────────────────────┼─────────────────────┘
                                ▼
                     ┌─────────────────────┐
                     │  Candidate Results   │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │  Context Processing  │
                     │  (rank / filter by   │
                     │   min_similarity)    │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │    LLM Generation    │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │   Final Solution     │
                     │     + Sources        │
                     └─────────────────────┘
```

**Layered backend:**

```
FastAPI
│
├── Routes           → HTTP surface, request/response schemas
│
├── Controllers
│   ├── NlpController               → ranking, answer generation, feedback sentiment
│   ├── SearchOrchestratorController → fans out to all retrieval sources
│   ├── StackoverflowscearchController
│   ├── GithubSearchController
│   └── ProcessController
│
├── Models            → MongoDB access layer (Answers, Errors, Jobs, Feedback)
│
├── Stores
│   ├── LLM factory
│   ├── Vector DB client (Qdrant)
│   ├── Classifiers
│   ├── Cache (Redis)
│   └── Prompt templates
│
└── Infrastructure    → MongoDB, Redis, Qdrant
```

---

## API Reference

All routes are served under the `/Fixflow-V1` prefix.

### NLP & Answers — `/Fixflow-V1/nlp`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/nlp/similar/{error_id}` | Finds and ranks web results similar to a stored error, using Redis to cache results |
| `POST` | `/nlp/answer/{error_id}` | Retrieves context (cached or fresh search) and generates an LLM-backed answer, persisting it with automatic versioning |
| `POST` | `/nlp/answer/{error_id}/feedback` | Records user feedback (text + score) on an answer, running sentiment analysis to compute a final rating |

**`POST /nlp/answer/{error_id}`** accepts a query parameter and a JSON body:

```
POST /Fixflow-V1/nlp/answer/{error_id}?force_refresh=true
Content-Type: application/json

{
  "pagesize": 5,
  "min_similarity": 0.5,
  "limit": 10
}
```

- `force_refresh` (query param, default `false`) — when `true`, bypasses both the cached DB answer and the cached search results, and **widens the retrieval scope** (lower similarity threshold, higher result limit) so a regeneration actually explores a broader set of evidence instead of repeating the exact same narrow query.

**`POST /nlp/answer/{error_id}/feedback`** body:

```json
{
  "feedback_text": "This didn't fully solve my issue",
  "score": 2
}
```

A `rating < 3` is treated as a signal that the stored answer needs improvement.

### Data — `/Fixflow-V1/data`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/data/upload/` | Submits a new raw error/query for processing |
| `GET`  | `/data/search/{error_id}` | Looks up a previously submitted error by ID |

> Interactive, always-up-to-date documentation is available via Swagger UI once the server is running, at **`/docs`**.

---

## Project Structure

```
FixFlow/
│
├── docker/
│   ├── .env.example
│   └── docker-compose.yaml
│
├── notebooks/                  # data exploration / experimentation
│
├── src/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── controllers/
│   │   ├── BaseController.py
│   │   ├── BaseSearchController.py
│   │   ├── DataController.py
│   │   ├── GithubSearchController.py
│   │   ├── NlpController.py
│   │   ├── ProcessController.py
│   │   ├── SearchOrchestratorController.py
│   │   ├── StackoverflowscearchController.py
│   │   └── extraction_parsing.py
│   │
│   ├── helper/
│   │   └── config.py
│   │
│   ├── models/
│   │   ├── AnswersModel.py
│   │   ├── ClusterModel.py
│   │   ├── DataBaseModel.py
│   │   ├── ErrorQueryModel.py
│   │   ├── FeedbackModel.py
│   │   └── JobProcessingModel.py
│   │
│   ├── routes/
│   │   ├── base.py
│   │   ├── nlp.py
│   │   └── schema/
│   │
│   └── stores/
│       ├── Cache/
│       ├── classifiers/
│       ├── llm/
│       ├── templetes/
│       └── vectordb/
│
├── README.md
└── LICENSE
```

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python, FastAPI, Uvicorn, Pydantic, MongoDB (Motor) |
| **AI / NLP** | PyTorch, Transformers, Sentence-Transformers, LangChain, Hugging Face, TextBlob, BitsAndBytes |
| **LLM** | Groq, Hugging Face-compatible models (via a factory abstraction) |
| **Retrieval** | Qdrant, sentence embeddings, vector similarity search, Stack Overflow, GitHub |
| **Infrastructure** | MongoDB, Redis, Qdrant, Docker, Docker Compose |

---

## Getting Started

### Requirements

- Python 3.10+
- Miniconda (or any virtualenv tool)
- Docker & Docker Compose
- Git

### System Dependencies (Ubuntu / WSL)

```bash
sudo apt update
sudo apt install libpq-dev gcc python3-dev
```

### 1. Clone the repository

```bash
git clone https://github.com/kerlosmelad12/FixFlow-.git
cd FixFlow-
```

### 2. Create and activate a Conda environment

```bash
conda create -n fixflow python=3.10
conda activate fixflow
python --version
```

### 3. Install dependencies

```bash
cd src
pip install -r requirements.txt
```

---

## Configuration

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

```dotenv
LLM_API_KEY=your_api_key
MONGO_URI=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
```

> ⚠️ **Never commit your `.env` file or expose API keys publicly.**

---

## Running with Docker

FixFlow's infrastructure (MongoDB, Redis, Qdrant) is provisioned via Docker Compose.

```bash
cd docker
cp .env.example .env      # fill in service credentials
docker compose up -d
docker compose ps          # verify all services are healthy
```

### Start the API server

```bash
cd ../src
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

| Resource | URL |
|---|---|
| API base | `http://localhost:5000` |
| Swagger docs | `http://localhost:5000/docs` |

### Quick start (all steps combined)

```bash
conda create -n fixflow python=3.10
conda activate fixflow

git clone https://github.com/kerlosmelad12/FixFlow-.git
cd FixFlow-

cd src
pip install -r requirements.txt
cp .env.example .env

cd ../docker
cp .env.example .env
docker compose up -d

cd ../src
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

---

## Frontend Demo Client

A minimal static HTML/CSS/JS client is included for exercising the API by hand — uploading an error, fetching similar errors, generating an answer, and submitting feedback. Update `API_BASE` in `app.js` to point at your running server, then open `index.html` in a browser (or serve it with any static file server).

---

## Example Walkthrough

**Input**

```
I'm getting ModuleNotFoundError when importing a package
after installing it with pip.
```

**Pipeline**

```
Raw Query → NLP Processing → Technology/Error Identification
          → Semantic Retrieval → Stack Overflow/GitHub Search
          → Candidate Processing → Context Construction
          → LLM Generation → Final Answer + Sources
```

**Response**

```
The package may have been installed in a different Python
environment from the one running your application.

Try:
  python -m pip install <package>

Then verify:
  python -c "import <package>"
```

---

## Engineering Principles

- **Retrieval before generation** — `Retrieve → Process → Generate`, never `Generate and hope`.
- **Modular AI components** — embedding, classification, retrieval, generation, and caching are independently swappable.
- **Factory-based providers** — LLM and classifier backends are abstracted so the provider can change without rewriting application logic.
- **Separation of concerns** — `Routes → Controllers → Stores/AI components → Infrastructure`.

---

## Current Limitations

- Retrieval quality is bounded by embedding quality.
- External APIs (Stack Overflow, GitHub) can introduce rate limits.
- LLM generation can still produce incorrect assumptions even with grounding.
- Technical sources can become outdated over time.
- Retrieval thresholds (`min_similarity`, `limit`) require ongoing tuning.
- A larger evaluation benchmark is needed for robust production-quality measurement.

---

## Roadmap

- Hybrid BM25 + semantic retrieval
- Cross-encoder reranking
- Query rewriting
- Conversation-aware debugging
- Repository-aware retrieval and code-context extraction
- Multi-step agentic debugging
- Automated retrieval evaluation and LLM-as-a-judge scoring
- Observability, tracing, and retrieval-latency monitoring
- CI/CD integration and automated regression testing

---

## Author

**Kerlos Melad** — AI / Machine Learning Engineer
GitHub: [@kerlosmelad12](https://github.com/kerlosmelad12)

---

## License

This project is licensed under the **MIT License**. See [`LICENSE`](./LICENSE) for details.

---

<div align="center">

*"Don't make the LLM guess the solution. Retrieve the evidence, understand the problem, and then generate the fix."*

</div>
