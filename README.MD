# FixFlow 🔧

> **AI-powered developer assistant for understanding, searching, and resolving software errors.**

FixFlow is an AI-driven developer support system that transforms raw error messages and technical problems into **context-aware, evidence-backed solutions**.

Instead of relying on a single LLM response, FixFlow combines **NLP processing, semantic search, vector retrieval, external knowledge sources, classification, caching, and LLM-based generation** to retrieve relevant technical knowledge and synthesize actionable solutions.

The system follows a **Retrieval-Augmented Generation (RAG)** architecture to ground generated answers in retrieved technical knowledge.

---

## 🎯 Problem

Developers often spend significant time debugging issues by:

* Searching Stack Overflow manually
* Searching GitHub repositories and issues
* Finding similar error messages
* Identifying the correct technology or framework
* Comparing multiple solutions
* Filtering irrelevant or outdated results

Traditional keyword search can fail when the developer describes a problem differently from how it appears in existing technical content.

**FixFlow addresses this problem through semantic retrieval, NLP-based understanding, multi-source search, and LLM-powered answer generation.**

---

# 🚀 Key Features

* 🧠 **NLP-based error understanding**
* 🏷️ **Technology / tag classification**
* 🔎 **Semantic vector search**
* 📚 **Retrieval-Augmented Generation (RAG)**
* 💬 **Stack Overflow search**
* 🐙 **GitHub search**
* 🤖 **LLM-powered solution generation**
* 🔗 **Source tracing**
* 🛡️ **Confidence-aware answer processing**
* ⚡ **Redis caching**
* 🗄️ **MongoDB persistence**
* 🧩 **Modular provider architecture**
* 🚀 **FastAPI backend**
* 🐳 **Docker-based infrastructure**

---

# 🧠 System Architecture

```text
                         ┌─────────────────────┐
                         │     User Query      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   NLP Processing    │
                         │                     │
                         │ • Error Extraction  │
                         │ • Entity Extraction │
                         │ • Tag Prediction    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │     Search Orchestrator      │
                    └──────────────┬───────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
       ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
       │   Qdrant    │      │    Stack    │      │   GitHub    │
       │ Vector DB   │      │   Overflow  │      │   Search    │
       └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │ Candidate Results   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Context Processing  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    LLM Generation   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Final Solution      │
                         │ + Sources           │
                         └─────────────────────┘
```

---

# 🔄 End-to-End Workflow

A typical FixFlow request follows this pipeline:

```text
User Problem
     │
     ▼
API Request
     │
     ▼
NLP Processing
     │
     ├── Error Extraction
     ├── Entity Extraction
     └── Technology Classification
     │
     ▼
Search Orchestration
     │
     ├── Semantic Vector Search
     ├── Stack Overflow Search
     └── GitHub Search
     │
     ▼
Candidate Aggregation
     │
     ▼
Relevance Processing
     │
     ▼
Context Construction
     │
     ▼
LLM Generation
     │
     ▼
Grounded Answer
     │
     ▼
Sources / Confidence
```

The architecture separates **query understanding, retrieval, processing, and generation** instead of sending the raw user query directly to an LLM.

---

# 🔍 Retrieval-Augmented Generation

FixFlow uses RAG to retrieve relevant technical knowledge before generating an answer.

Instead of:

```text
User → LLM → Answer
```

the system follows:

```text
User
 ↓
Understand Query
 ↓
Retrieve Evidence
 ↓
Process Context
 ↓
LLM
 ↓
Grounded Answer
```

This approach helps reduce the model's dependence on its internal knowledge and provides relevant technical context during generation.

---

# 🧩 Core Components

## 1. NLP Processing

The NLP layer processes the incoming technical problem and extracts useful information such as:

* Error messages
* Technical entities
* Technologies
* Relevant tags
* Problem-related information

This structured representation improves the downstream search process.

---

## 2. Technology Classification

FixFlow includes a classifier component for identifying technologies associated with a problem.

For example:

```text
Input:
"Gradle build fails after upgrading Kotlin"

Possible technologies:

Kotlin
Gradle
Android
```

The classifier is initialized through the project's classifier factory architecture.

---

## 3. Semantic Search

FixFlow uses sentence embeddings to represent technical queries semantically.

The system uses:

* Sentence Transformers
* PyTorch
* Vector similarity search
* Qdrant

Semantic retrieval allows the system to find technically similar content even when the wording is different.

For example:

```text
"python cannot find installed package"
```

can retrieve content related to:

```text
"ModuleNotFoundError after installing a dependency"
```

---

## 4. Search Orchestration

Search operations are coordinated through a dedicated search orchestration layer.

The orchestration process separates:

```text
Query Understanding
        ↓
Search Strategy
        ↓
Candidate Retrieval
        ↓
Result Processing
        ↓
Answer Generation
```

This makes the retrieval layer easier to extend with additional sources or search strategies.

---

## 5. Stack Overflow Integration

Stack Overflow provides real-world developer questions and answers.

It is particularly useful for:

* Runtime errors
* Dependency problems
* Framework issues
* Configuration problems
* Common development errors

---

## 6. GitHub Integration

GitHub provides another source of technical knowledge from real repositories and development environments.

The system can search for relevant information including:

* Similar implementation problems
* Repository issues
* Configuration examples
* Real-world fixes
* Framework-specific solutions

---

## 7. Answer Fusion

Retrieved results can contain multiple solutions or partially overlapping information.

FixFlow processes retrieved knowledge before presenting the final response.

The objective is to transform multiple retrieved results into a **single useful and actionable solution**.

---

## 8. Confidence Guard

FixFlow includes a confidence-aware layer intended to prevent low-quality retrieval results from being blindly used as the final answer.

This provides an additional control layer between retrieval and answer generation.

---

## 9. Source Tracing

FixFlow keeps track of retrieved technical sources so that generated answers can be associated with their underlying evidence.

This improves transparency compared with a standalone LLM chatbot.

---

# 🤖 LLM Architecture

LLM components are abstracted through a factory-based architecture.

This separates the application logic from the underlying model provider.

Conceptually:

```text
Application
     │
     ▼
LLM Factory
     │
     ▼
Generation Provider
```

The project supports an architecture that can work with different LLM backends without tightly coupling the application to one provider.

The dependency stack includes integrations such as:

* Hugging Face
* Transformers
* LangChain
* Groq
* PyTorch
* BitsAndBytes

---

# 🗄️ Storage Architecture

FixFlow uses different storage systems for different responsibilities.

| Component      | Responsibility                       |
| -------------- | ------------------------------------ |
| MongoDB        | Application and document persistence |
| Qdrant         | Vector similarity search             |
| Redis          | Caching                              |
| Stack Overflow | External technical knowledge         |
| GitHub         | External technical knowledge         |

This separation allows each infrastructure component to focus on its specific workload.

---

# ⚡ Caching

Redis is used as the caching layer.

Caching can reduce repeated expensive operations such as:

* Repeated queries
* External search requests
* Repeated retrieval operations
* Frequently requested information

This becomes particularly useful as query volume increases.

---

# 🏗️ Backend Architecture

FixFlow is implemented as a modular FastAPI backend.

```text
FastAPI
│
├── Routes
│
├── Controllers
│   ├── Data Controller
│   ├── NLP Controller
│   ├── Search Controllers
│   ├── Search Orchestrator
│   └── Processing Controllers
│
├── Models
│
├── Stores
│   ├── LLM
│   ├── Vector DB
│   ├── Classifiers
│   ├── Cache
│   └── Templates
│
└── Infrastructure
    ├── MongoDB
    ├── Redis
    └── Qdrant
```

This structure follows a separation-of-concerns approach where the API layer is separated from business logic, AI components, and infrastructure.

---

# 📁 Project Structure

```text
FixFlow/
│
├── docker/
│   ├── .env.example
│   ├── .gitignore
│   └── docker-compose.yaml
│
├── notebooks/
│   └── Data exploration / experimentation
│
├── src/
│   │
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
│   │   └── schema/
│   │
│   └── stores/
│       ├── Cache/
│       ├── classifiers/
│       ├── llm/
│       ├── templetes/
│       └── vectordb/
│
├── README.MD
└── LICIENSE
```

---

# 🛠️ Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn
* Pydantic
* MongoDB

### AI / NLP

* PyTorch
* Transformers
* Sentence Transformers
* LangChain
* Hugging Face
* TextBlob
* BitsAndBytes

### LLM

* Groq
* Hugging Face-compatible models

### Retrieval

* Qdrant
* Sentence embeddings
* Vector similarity search
* Stack Overflow
* GitHub

### Infrastructure

* MongoDB
* Redis
* Qdrant
* Docker
* Docker Compose

---

# 🚀 Getting Started

## Requirements

* Python 3.10 or later
* Miniconda
* Docker
* Docker Compose
* Git

---

## System Dependencies

On Ubuntu / WSL:

```bash
sudo apt update
sudo apt install libpq-dev gcc python3-dev
```

---

## Install Python Using Miniconda

Create a dedicated Conda environment:

```bash
conda create -n fixflow python=3.10
```

Activate the environment:

```bash
conda activate fixflow
```

Verify the Python version:

```bash
python --version
```

---

## Clone the Repository

```bash
git clone https://github.com/kerlosmelad12/FixFlow-.git
cd FixFlow-
```

---

## Install Dependencies

Move into the source directory:

```bash
cd src
```

Install the required packages:

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create the environment file:

```bash
cp .env.example .env
```

Update `.env` with the required configuration and API credentials.

Example:

```env
LLM_API_KEY=your_api_key
```

> **Never commit your `.env` file or expose API keys publicly.**

---

# 🐳 Run Docker Compose Services

Move to the Docker directory:

```bash
cd ../docker
```

Create the Docker environment file:

```bash
cp .env.example .env
```

Update `.env` with the required service configuration and credentials.

Start the infrastructure:

```bash
docker compose up -d
```

Check running services:

```bash
docker compose ps
```

---

# 🚀 Run the FastAPI Server

Move back to the source directory:

```bash
cd ../src
```

Start the FastAPI application:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

The API will be available at:

```text
http://localhost:5000
```

FastAPI Swagger documentation:

```text
http://localhost:5000/docs
```

---

# 🔎 Verify the Application

Open:

```text
http://localhost:5000/docs
```

The Swagger UI allows you to explore and test the available FixFlow endpoints.

---

# ⚡ Quick Start

For a clean setup:

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

FixFlow should now be running locally.

---

# 🧪 Example

### Input

```text
I'm getting ModuleNotFoundError when importing a package
after installing it with pip.
```

### Processing

```text
Raw Query
    ↓
NLP Processing
    ↓
Technology / Error Identification
    ↓
Semantic Retrieval
    ↓
Stack Overflow / GitHub Search
    ↓
Candidate Processing
    ↓
Context Construction
    ↓
LLM Generation
    ↓
Final Answer + Sources
```

### Example Response

```text
The package may have been installed in a different
Python environment from the one running your application.

Try:

python -m pip install <package>

Then verify the installation:

python -c "import <package>"
```

The final answer is generated using the retrieved technical context.

---

# 🔐 Engineering Principles

## Retrieval Before Generation

FixFlow follows:

```text
Retrieve → Process → Generate
```

rather than:

```text
Generate → Hope the answer is correct
```

---

## Modular AI Components

The system separates:

* Embedding
* Classification
* Retrieval
* Generation
* Caching
* Storage

This makes individual components easier to replace or improve.

---

## Factory-Based Providers

Provider-specific components are abstracted behind factory patterns.

This allows the application to change models or providers without rewriting the complete application layer.

---

## Separation of Concerns

The architecture separates:

```text
Routes
   ↓
Controllers
   ↓
Stores / AI Components
   ↓
Infrastructure
```

This improves maintainability and extensibility.

---

# 📊 Evaluation Strategy

A production-oriented version of FixFlow should evaluate the system at multiple levels.

### Retrieval Evaluation

* Recall@K
* Precision@K
* MRR
* nDCG

### Generation Evaluation

* Answer relevance
* Faithfulness
* Context utilization
* Source correctness

### System Evaluation

* End-to-end latency
* Retrieval latency
* LLM latency
* Cache hit rate
* API error rate

Separating retrieval evaluation from generation evaluation makes it easier to identify where system quality is improving or degrading.

---

# ⚠️ Current Limitations

FixFlow is an evolving AI engineering project.

Current limitations include:

* Retrieval quality depends on embedding quality
* External APIs may introduce rate limits
* LLMs can still produce incorrect assumptions
* Technical sources may become outdated
* Retrieval thresholds require tuning
* A larger evaluation benchmark is required for robust production evaluation

---

# 🛣️ Future Improvements

Potential improvements include:

* Hybrid BM25 + semantic retrieval
* Cross-encoder reranking
* Query rewriting
* Conversation-aware debugging
* Repository-aware retrieval
* Code-context extraction
* Multi-step agentic debugging
* Automated retrieval evaluation
* LLM-as-a-judge evaluation
* Observability and tracing
* Retrieval latency monitoring
* CI/CD integration
* Automated regression testing

---

# 🔮 Future Vision

The long-term goal is to evolve FixFlow from a technical answer retrieval system into an intelligent debugging platform.

```text
                  Developer
                      │
                      ▼
                FixFlow Agent
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
     Search        Analyze       Retrieve
        │             │             │
        ▼             ▼             ▼
   Web / GitHub    Codebase      Knowledge
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                Reasoning Layer
                      │
                      ▼
                Proposed Fix
                      │
                      ▼
                 Verification
                      │
                      ▼
              Final Recommendation
```

The vision is to move from:

> **"Here is a possible answer."**

to:

> **"I investigated the problem, retrieved relevant evidence, proposed a fix, and verified the solution."**

---

# 👨‍💻 Author

**Kerlos Melad**

AI / Machine Learning Engineer

GitHub: `kerlosmelad12`

---

# 📄 License

This project is licensed under the **MIT License**.

See [`LICIENSE`](./LICIENSE) for details.

---

## ⭐ Project Philosophy

> **Don't make the LLM guess the solution.
> Retrieve the evidence, understand the problem, and then generate the fix.**

FixFlow is built around this principle.
