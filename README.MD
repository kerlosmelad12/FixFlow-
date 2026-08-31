# FixFlow 🔧

> **AI-powered developer assistant for understanding, searching, and resolving software errors.**

FixFlow is an AI-driven developer support system that transforms raw error messages and technical problems into **context-aware, evidence-backed solutions**.

Instead of relying on a single LLM response, FixFlow combines **NLP preprocessing, semantic search, vector retrieval, external knowledge sources, classification, caching, and LLM-based generation** to retrieve relevant technical knowledge and synthesize a concise solution.

The system is designed around a **Retrieval-Augmented Generation (RAG)** workflow to reduce hallucinations and ground generated answers in retrieved technical content.

---

## 🎯 Problem

Developers frequently spend significant time debugging issues by:

* Searching Stack Overflow manually
* Going through multiple GitHub repositories and issues
* Comparing similar error messages
* Identifying the correct framework or technology involved
* Filtering outdated or irrelevant solutions
* Combining multiple answers into one actionable fix

Traditional keyword search often fails when the developer's wording differs from the wording used in existing solutions.

FixFlow addresses this by combining **semantic retrieval + NLP-based understanding + external search + LLM synthesis**.

---

# 🚀 What FixFlow Does

Given a technical problem such as:

```text
ModuleNotFoundError: No module named 'pydantic_settings'
```

FixFlow processes the query through multiple stages:

```text
User Problem
     │
     ▼
NLP Processing
     │
     ├── Error / Entity Extraction
     ├── Text Understanding
     └── Technology / Tag Prediction
     │
     ▼
Search Orchestration
     │
     ├── Vector Search
     ├── Stack Overflow Search
     └── GitHub Search
     │
     ▼
Candidate Retrieval
     │
     ▼
Relevance Filtering / Ranking
     │
     ▼
Context Construction
     │
     ▼
LLM Generation
     │
     ▼
Grounded Solution
     │
     ▼
Sources + Confidence
```

The main goal is not simply to generate an answer, but to **retrieve useful evidence first and then generate an answer grounded in that evidence**.

---

# 🧠 Core AI Architecture

FixFlow follows a modular AI pipeline:

```text
                         ┌─────────────────────┐
                         │      User Query     │
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
       │ Vector DB   │      │ Stack       │      │ GitHub      │
       │   Search    │      │ Overflow    │      │ Search      │
       └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │ Candidate Answers   │
                         │ & Technical Context │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   RAG Generation    │
                         │                     │
                         │   Context + Query   │
                         │        + LLM        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Final Solution      │
                         │ + Evidence/Sources  │
                         └─────────────────────┘
```

---

# 🔍 Retrieval-Augmented Generation

The core of FixFlow is a RAG-based architecture.

Instead of asking the LLM to solve an error from its internal knowledge alone, FixFlow first retrieves relevant technical information.

### Retrieval

The system converts the user query into an embedding representation and searches the vector database for semantically similar technical content.

This allows queries such as:

```text
"python cannot find module after installing package"
```

to retrieve solutions containing different wording such as:

```text
"ModuleNotFoundError when importing installed dependency"
```

even when the exact keywords do not match.

### Generation

Retrieved context is then passed to the generation model.

Conceptually:

```text
Answer = LLM(
    User Query
    +
    Retrieved Technical Context
)
```

This makes the generation stage more grounded and reduces the dependency on the model's parametric knowledge.

---

# 🧩 AI Components

## 1. NLP Processing

FixFlow contains a dedicated NLP layer responsible for transforming raw technical input into structured information.

The NLP pipeline can identify useful information such as:

* Error messages
* Error patterns
* Technology names
* Versions
* Technical entities
* Relevant tags

This structured representation improves downstream retrieval.

---

## 2. Tag / Technology Classification

FixFlow includes a classifier component used to identify the technologies relevant to the incoming problem.

For example:

```text
Input:
"Gradle build fails after upgrading Kotlin"

Predicted technologies:

Kotlin
Gradle
Android
```

These predictions can be used to improve search relevance and narrow down the candidate knowledge space.

The classifier is loaded during application startup through the classifier factory and its associated encoder/label-encoder components.

---

## 3. Semantic Search

Keyword matching is insufficient for technical troubleshooting because two developers can describe the same problem using completely different language.

FixFlow therefore uses **sentence embeddings** to represent technical queries semantically.

The project uses:

* `sentence-transformers`
* `torch`
* Vector database retrieval
* Configurable distance metrics

The vector database layer is initialized through a dedicated factory abstraction.

---

## 4. Search Orchestration

Search is not implemented as a single retrieval call.

FixFlow contains a dedicated `SearchOrchestratorController` responsible for coordinating the search workflow.

The architecture separates:

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

This separation makes it easier to add or replace retrieval sources without coupling them directly to the API layer.

---

## 5. Stack Overflow Search

Stack Overflow acts as one of the primary external technical knowledge sources.

FixFlow can search existing questions and answers to retrieve real developer discussions and previously validated solutions.

This is particularly useful for:

* Framework errors
* Dependency issues
* Runtime exceptions
* Configuration problems
* Build failures

---

## 6. GitHub Search

FixFlow also integrates GitHub-based search to retrieve technical information from real repositories.

This provides another source of evidence beyond Q&A datasets and allows the system to discover:

* Similar implementation problems
* Repository-specific fixes
* Configuration examples
* Real-world usage patterns

---

## 7. Answer Processing

Retrieved results can contain:

* Duplicate information
* Partial solutions
* Multiple approaches
* Conflicting answers
* Irrelevant results

FixFlow therefore separates retrieval from final response generation.

The goal is to transform multiple retrieved documents into a **single actionable technical response** instead of simply returning a list of search results.

---

# 🤖 LLM Architecture

LLM access is abstracted behind a factory-based architecture.

The application initializes both:

```text
Embedding Backend
        │
        ▼
   LLM Factory

Generation Backend
        │
        ▼
   LLM Factory
```

This separation allows the embedding and generation models to be configured independently.

The current implementation initializes the embedding model and generation model separately during application startup.

The project also includes:

* Hugging Face integrations
* LangChain
* Groq
* Transformers
* Accelerate
* BitsAndBytes

according to the project's dependency configuration.

---

# 🗄️ Data & Storage Architecture

FixFlow uses multiple storage technologies for different responsibilities.

| Component        | Responsibility                     |
| ---------------- | ---------------------------------- |
| MongoDB          | Application / document persistence |
| Qdrant           | Vector similarity search           |
| Redis            | Caching                            |
| External Sources | Stack Overflow / GitHub knowledge  |
| LLM              | Solution synthesis                 |

This separation allows each storage system to focus on the workload it is best suited for.

---

# ⚡ Caching

Redis is integrated into the application through a dedicated cache controller.

The cache layer is initialized during application startup and exposed to the rest of the application through the application context.

Caching is useful for reducing repeated work for:

* Frequently requested queries
* Repeated searches
* Expensive external API requests
* Repeated retrieval operations

---

# 🏗️ Backend Architecture

FixFlow is implemented as a modular FastAPI backend.

The high-level structure is:

```text
FastAPI
│
├── Routes
│
├── Controllers
│   ├── NLP Controller
│   ├── Search Controllers
│   ├── Data Controller
│   └── Search Orchestrator
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
├── Helpers
│
└── External Services
    ├── MongoDB
    ├── Redis
    ├── Qdrant
    ├── Stack Overflow
    └── GitHub
```

The repository reflects this separation through dedicated `controllers`, `models`, `routes`, `helper`, and `stores` packages.

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
* Async MongoDB with Motor

### AI / NLP

* PyTorch
* Transformers
* Sentence Transformers
* LangChain
* Hugging Face
* TextBlob
* BitsAndBytes

### LLM Providers

* Groq
* Hugging Face-compatible models

### Retrieval

* Qdrant
* Semantic embeddings
* Vector similarity search
* Stack Overflow
* GitHub

### Infrastructure

* MongoDB
* Redis
* Docker / Docker Compose

The main dependencies and versions are explicitly pinned in `src/requirements.txt`.

---

# 🚀 Getting Started

## Prerequisites

Make sure you have:

* Python 3.10+
* Docker
* Docker Compose
* Git
* Access credentials for the configured LLM / external APIs

---

## 1. Clone the Repository

```bash
git clone https://github.com/kerlosmelad12/FixFlow-.git

cd FixFlow-
```

---

## 2. Configure Environment Variables

Copy the environment template:

```bash
cp docker/.env.example docker/.env
```

Configure the required values for:

```text
MongoDB
Redis
Qdrant
LLM provider
Embedding backend
Generation backend
External search APIs
```

Do not commit real API keys to the repository.

---

## 3. Start Infrastructure

From the Docker directory:

```bash
cd docker

docker compose up -d
```

This starts the infrastructure required by the application according to the project's Docker configuration.

---

## 4. Install Python Dependencies

```bash
cd ../src

python -m venv .venv
```

Activate the environment.

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 5. Start the API

From `src/`:

```bash
python main.py
```

The FastAPI application starts through Uvicorn on:

```text
http://localhost:5000
```

The application configures its routes and initializes the LLM, classifier, vector database, Redis, MongoDB, and template components during startup.

---

# 🔄 Request Lifecycle

A typical FixFlow request follows this flow:

```text
1. User submits technical problem
             │
             ▼
2. API receives request
             │
             ▼
3. NLP preprocessing
             │
             ├── Error extraction
             ├── Entity extraction
             └── Technology classification
             │
             ▼
4. Search orchestration
             │
             ├── Vector search
             ├── Stack Overflow
             └── GitHub
             │
             ▼
5. Candidate aggregation
             │
             ▼
6. Relevance filtering
             │
             ▼
7. Context construction
             │
             ▼
8. LLM generation
             │
             ▼
9. Final answer
             │
             └── Supporting sources
```

This architecture intentionally separates **retrieval from generation**, which makes the system easier to debug and extend.

---

# 🧪 Example

### Input

```text
I'm getting ModuleNotFoundError when importing a package
after installing it with pip.
```

### Internal Processing

```text
Raw Query
   ↓
NLP Processing
   ↓
Technology / Error Identification
   ↓
Semantic Retrieval
   ↓
External Search
   ↓
Relevant Technical Context
   ↓
LLM Synthesis
```

### Expected Output

```text
The package is likely installed in a different Python
environment from the one running your application.

Try:

python -m pip install <package>

Then verify:

python -c "import <package>"
```

The final response can be grounded in retrieved technical sources instead of being generated purely from the model's internal knowledge.

---

# 🔐 Design Principles

FixFlow is built around several engineering principles.

### 1. Retrieval Before Generation

The LLM should receive relevant evidence whenever possible.

```text
Retrieve → Filter → Generate
```

rather than:

```text
Generate → Hope it's correct
```

---

### 2. Modular AI Components

The system separates:

* Embedding
* Classification
* Retrieval
* Generation
* Caching
* Storage

This reduces coupling and allows individual components to evolve independently.

---

### 3. Factory-Based Providers

LLM, classifier, and vector database components are instantiated through factory abstractions.

This makes provider changes configuration-driven rather than requiring major changes to application logic.

---

### 4. Evidence-Grounded Generation

The goal is to produce answers based on retrieved technical knowledge rather than relying exclusively on model knowledge.

---

### 5. Separation of Concerns

The backend separates:

```text
Routes
   ↓
Controllers
   ↓
Stores / Services
   ↓
Infrastructure
```

This makes the codebase easier to maintain and extend.

---

# 📈 Why This Architecture?

A simple chatbot would be:

```text
User → LLM → Answer
```

FixFlow instead uses:

```text
User
 ↓
NLP
 ↓
Retrieval
 ├── Vector DB
 ├── Stack Overflow
 └── GitHub
 ↓
Context
 ↓
LLM
 ↓
Grounded Answer
```

This architecture provides several advantages:

* Better grounding
* Better retrieval of domain-specific knowledge
* Reduced hallucination risk
* More transparent answers
* Easier debugging
* Replaceable AI components
* Multiple knowledge sources
* Better extensibility

---

# 🔬 Engineering Trade-offs

## Vector Search vs Keyword Search

### Keyword Search

**Advantages**

* Simple
* Fast
* Easy to implement

**Limitations**

* Sensitive to wording
* Weak semantic understanding
* Poor handling of paraphrased queries

### Semantic Search

**Advantages**

* Captures semantic similarity
* Handles different wording
* Better suited for natural-language technical questions

**Trade-off**

* Requires embedding computation
* Requires vector infrastructure
* Requires careful similarity thresholds

FixFlow chooses semantic retrieval because technical problems are often described differently by different developers.

---

# 🧱 Extensibility

The current architecture makes it possible to add additional providers or retrieval sources.

Potential extensions include:

```text
Additional Vector DB
        │
        ▼
New Search Provider
        │
        ▼
Additional LLM Provider
        │
        ▼
Additional Classifier
```

without redesigning the complete API layer.

---

# 🛣️ Future Improvements

Potential improvements include:

* Hybrid BM25 + semantic retrieval
* Cross-encoder reranking
* Better retrieval evaluation
* Query rewriting
* Conversation-aware debugging
* Multi-step agentic debugging
* Automatic code-context extraction
* Repository-aware retrieval
* More robust source quality scoring
* LLM-as-a-judge evaluation
* Observability and tracing
* Retrieval latency monitoring
* Automated regression evaluation
* CI/CD integration

---

# 📊 Evaluation Strategy

A production-grade version of FixFlow should evaluate the system at multiple levels.

### Retrieval

Measure:

* Recall@K
* Precision@K
* MRR
* nDCG

### Generation

Measure:

* Faithfulness
* Answer relevance
* Context utilization
* Citation / source correctness

### System

Measure:

* End-to-end latency
* Retrieval latency
* LLM latency
* Cache hit rate
* API error rate

This separates **retrieval quality** from **generation quality**, making it easier to identify where the system needs improvement.

---

# ⚠️ Current Limitations

FixFlow is an evolving AI engineering project.

Current limitations include:

* Retrieval quality depends on embedding quality
* External search APIs may have rate limits
* LLM responses can still contain incorrect assumptions
* Technical sources can become outdated
* Retrieval thresholds require tuning
* End-to-end evaluation needs a larger benchmark dataset

These are important considerations for moving the system from a prototype toward a production-grade developer platform.

---

# 🔮 Long-Term Vision

The long-term goal of FixFlow is to evolve from a **technical answer retrieval system** into an intelligent debugging platform.

A future architecture could look like:

```text
                 Developer
                     │
                     ▼
              FixFlow Agent
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
     Search       Analyze       Retrieve
        │            │            │
        ▼            ▼            ▼
   Web / GitHub   Codebase     Knowledge
        │            │            │
        └────────────┼────────────┘
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

This would allow FixFlow to move beyond answering questions and toward **actually investigating and validating software failures**.

---

# 👨‍💻 Author

**Kerlos Melad**

AI / Machine Learning Engineer

* GitHub: [@kerlosmelad12](https://github.com/kerlosmelad12)

---

# 📄 License

This project is licensed under the **MIT License**.

See [`LICIENSE`](./LICIENSE) for details.

---

## ⭐ Project Philosophy

> **Don't make the LLM guess the solution.
> Retrieve the evidence, understand the problem, and then generate the fix.**

FixFlow is built around this principle.
