<div align="center">

# 🔧 FixFlow

### *The Intelligent Developer Assistant for Resolving Software Errors*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICIENSE)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B%20%7C%2020%2B-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Supported-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

**Paste any error message or stack trace → FixFlow automatically extracts the error type, retrieves matching solutions from developer sources, and generates an evidence-grounded fix.**

[Quick Start](#-quick-start-3-simple-steps) • [Web UI Guide](#-how-to-use-the-web-ui) • [API Reference](#-api-endpoints) • [Troubleshooting](#-troubleshooting--faq)

</div>

---

## 📖 What is FixFlow?

When software breaks, developers usually spend 20–40 minutes searching Stack Overflow, reading outdated answers, and guessing what went wrong. 

**FixFlow automates this entire debugging workflow:**
1. **Understands the Error:** Automatically identifies whether it's a `TypeError`, `SyntaxError`, `ImportError`, or database failure.
2. **Searches Context:** Matches the issue against real developer discussions, Stack Overflow Q&As, and GitHub issues.
3. **Generates Grounded Solutions:** Synthesizes an actionable step-by-step fix with corrected code snippets, backed by real sources.
4. **Adaptive Feedback Loop:** If a generated fix doesn't work, submitting feedback automatically refines and regenerates a better answer.

```
┌─────────────────┐      ┌─────────────────────────┐      ┌───────────────────────────┐
│ Paste Any Error │ ───► │ Understand & Categorize │ ───► │ Instant Fix + Code Snippet │
└─────────────────┘      └─────────────────────────┘      └───────────────────────────┘
```

---

## 🚀 Quick Start (3 Simple Steps)

You don't need any complex AI or database knowledge to run FixFlow on your machine. Just follow these 3 commands:

### 1. Clone the repository
Open your terminal (macOS/Linux) or Command Prompt / PowerShell (Windows), and run:
```bash
git clone https://github.com/kerlosmelad12/FixFlow-.git
cd FixFlow-
```

### 2. Install dependencies
Make sure you have [Node.js](https://nodejs.org/) installed (version 18 or newer), then run:
```bash
npm install
```

### 3. Start the application
```bash
npm start
```

🎉 **That's it!** Open your browser and navigate to:
👉 **[http://localhost:3000](http://localhost:3000)**

You will see the FixFlow dashboard ready to diagnose your code errors!

---

## 🖥️ How to Use the Web UI

The built-in web dashboard provides an interactive interface for debugging:

```
┌─────────────────────────────────────────────────────────────┐
│                   FixFlow Error Solver                      │
├─────────────────────────────────────────────────────────────┤
│ 1. Upload Error                                             │
│    [ Paste your traceback or error here...                ] │
│    [ Submit ]                                               │
│                                                             │
│ 2. Get Answer                                               │
│    [ Error ID: 9f8a3b... ]                                  │
│    [ Get Answer ]  [ Generate New Answer ]                  │
│                                                             │
│ 3. Submit Feedback                                          │
│    [ Rating 1-5 ] [ What worked or didn't work?         ]  │
│    [ Submit Feedback ]                                      │
│                                                             │
│ 4. Similar Errors                                           │
│    [ Find Similar StackOverflow & GitHub discussions ]      │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step Workflow:

1. **Submit an Error:**
   - In the **Upload Error** box, paste any error message, e.g.:
     ```
     TypeError: Cannot read properties of undefined (reading 'map')
     ```
   - Click **Submit**. FixFlow will assign a unique `error_id` and assign it to an error cluster (such as *Type Mismatch & Invocation*).
   - Copy the `error_id` from the result box.

2. **Get the Diagnosis & Fix:**
   - Paste your `error_id` into the **Get Answer** card.
   - Click **Get Answer**. You'll instantly receive:
     - 🔍 **Root Cause**: Exactly what caused the issue.
     - 📋 **Steps to Resolve**: Ordered, actionable bullet points.
     - 💻 **Code Fix**: A defensive copy-pasteable code sample.
     - 🔗 **References**: Links to related Stack Overflow searches.

3. **Provide Feedback (Self-Improving AI):**
   - Enter your `error_id` in the **Submit Feedback** card.
   - Enter your comments and score (1 to 5).
   - If you rate it **1 or 2 stars**, FixFlow will automatically detect the dissatisfaction and generate an improved alternative solution!

4. **Explore Similar Community Errors:**
   - Enter your `error_id` in the **Similar Errors** card.
   - Click **Find Similar** to see accepted answers from Stack Overflow and GitHub issues with similarity scores.

---

## ⚙️ Configuration (Optional)

FixFlow works out of the box with built-in heuristic diagnosis. If you want to enable deep AI generation using Google Gemini:

1. Create a `.env` file in the root folder:
   ```bash
   cp .env.example .env
   ```
2. Add your free Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   > 💡 *You can get a free API key at [Google AI Studio](https://aistudio.google.com/).*

---

## 🐍 Alternative: Running with Python & Docker

If you want to run the full Python microservice stack with Docker containers (MongoDB, Redis, and Qdrant):

### Prerequisites
- Python 3.10+
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 1. Launch the Infrastructure Services
```bash
cd docker
docker compose up -d
```
This spins up:
- **MongoDB** (`localhost:27017`) for persistent error & feedback storage.
- **Redis** (`localhost:6379`) for high-speed retrieval caching.
- **Qdrant** (`localhost:6333`) for high-dimensional vector search.

### 2. Set Up Python Backend
```bash
# Return to root and create a virtual environment
cd ..
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Start the Python FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

Interactive API documentation will be available at:
👉 **`http://localhost:5000/docs`**

---

## 🔌 API Endpoints

All endpoints are prefixed with `/Fixflow-V1`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/Fixflow-V1/` | Service health check and version info |
| `POST` | `/Fixflow-V1/data/upload/` | Ingests an error query, cleans text, and computes cluster |
| `GET` | `/Fixflow-V1/data/search/:error_id` | Checks processing status for an error |
| `DELETE` | `/Fixflow-V1/data/error/:error_id` | Deletes an error and associated answers |
| `POST` | `/Fixflow-V1/nlp/answer/:error_id` | Generates diagnostic fix, root-cause, and code fix |
| `POST` | `/Fixflow-V1/nlp/answer/:error_id/feedback` | Records user feedback and triggers regeneration if rating is low |
| `POST` | `/Fixflow-V1/nlp/similar/:error_id` | Retrieves ranked similar solutions from developer sources |

### Example API Usage with cURL:

**Upload an error:**
```bash
curl -X POST http://localhost:3000/Fixflow-V1/data/upload/ \
  -H "Content-Type: application/json" \
  -d '{"query": "TypeError: Cannot read properties of undefined (reading '\''map'\'')"}'
```

**Generate an answer:**
```bash
curl -X POST http://localhost:3000/Fixflow-V1/nlp/answer/<YOUR_ERROR_ID>
```

---

## 📁 Project Structure

```
FixFlow/
├── public/                  # Frontend user interface
│   ├── index.html           # Main dashboard layout
│   ├── style.css            # Clean UI styles
│   └── app.js               # Client-side API caller
├── server.js                # Full-stack API server & routing
├── metadata.json            # Application metadata
├── package.json             # Node dependencies and scripts
├── .env.example             # Configuration template
├── README.md                # Project documentation
└── LICIENSE                 # MIT License
```

---

## ❓ Troubleshooting & FAQ

<details>
<summary><b>Q: I get "command not found: npm" or "node is not recognized"</b></summary>
<br/>
You need to install Node.js. Download the LTS version from <a href="https://nodejs.org/">nodejs.org</a>. Once installed, restart your terminal and verify by typing <code>node -v</code> and <code>npm -v</code>.
</details>

<details>
<summary><b>Q: Port 3000 is already in use</b></summary>
<br/>
Another application is running on port 3000. You can stop the conflicting program or edit the <code>PORT</code> variable in <code>server.js</code> to another port (such as 3001 or 5000).
</details>

<details>
<summary><b>Q: Do I need to pay for Gemini API?</b></summary>
<br/>
No! Google AI Studio provides a generous free tier for developers. Simply visit <a href="https://aistudio.google.com/">ai.studio</a> to create your key and paste it into your <code>.env</code> file.
</details>

<details>
<summary><b>Q: Can I use FixFlow without an API key?</b></summary>
<br/>
Yes! FixFlow includes a built-in rule-based diagnostic engine that works completely offline without any API key required. Adding a Gemini API key simply upgrades answers to real-time generative reasoning.
</details>

---

## 👨‍💻 Author

**Kerlos Melad**  
- GitHub: [@kerlosmelad12](https://github.com/kerlosmelad12)  
- Email: kerlosmelad124@gmail.com  

---

## 📄 License

This project is open source and available under the [MIT License](./LICIENSE). Feel free to fork, customize, and contribute!
