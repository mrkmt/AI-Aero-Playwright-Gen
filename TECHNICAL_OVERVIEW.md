# AI-Aero-Playwright-Gen: Technical Overview 🚀

AI-Aero-Playwright-Gen is a professional-grade multi-agent platform designed for automated web testing. It combines manual recording with agentic AI orchestration to generate robust, self-healing Playwright scripts.

## 🏗️ System Architecture

### 1. Backend (Python/FastAPI)
The backend serves as the core orchestration engine, managing sessions, AI pipelines, and test execution.

- **FastAPI**: High-performance web framework for API endpoints.
- **Uvicorn**: ASGI server for running the FastAPI application.
- **LiteLLM**: Unified interface for routing prompts to multiple AI providers (OpenAI, Qwen, Ollama).
- **Smolagents**: Orchestrates the multi-agent "Architect-Coder-Reviewer" flow.
- **Playwright (Python)**: Used for the live recorder worker and test execution.
- **ChromaDB**: Vector search backend for the **Knowledge Hub** (RAG).
- **Pytest + Pytest-HTML**: Execution engine that produces professional test reports.

### 2. Frontend (React/TypeScript)
A modern, high-performance UI built with a focus on "Rich Aesthetics" and real-time monitoring.

- **React + Vite**: Fast development and optimized bundling.
- **TypeScript**: Ensures type safety and robust code structure.
- **Tailwind CSS**: Utility-first styling with modern dark-mode aesthetics.
- **Lucide React**: Vectorized icon set for the dashboard and menus.
- **Framer Motion**: Smooth micro-animations and transitions.

---

## 🤖 AI Intelligence Layer

The project employs a **Hybrid AI Pipeline** that balances speed, cost, and reliability.

### Models Used
- **Cloud Model**: `openai/qwen-coder-plus` (Primary for complex code and planning).
- **Local Model**: `llama3.2:3b` or `moondream:latest` (Fallback for offline use or quota limits).

### Multi-Agent Orchestration
When generating code, three specialized agents collaborate:
1.  **Agent A (Architect)**: Analyzes recording events and creates a logical test architecture.
2.  **Agent B (Coder)**: Implementation agent that writes the actual Python Playwright code.
3.  **Agent C (Reviewer)**: Senior automation reviewer that fixes unstable selectors and ensures `pytest` compatibility.

---

## 🛠️ Key Functions & Modules

### Backend (Python)
- `start_recording()`: Spawns a Playwright browser thread to capture user actions in real-time.
- `generate_playwright_code()`: The entry point for the Multi-Agent flow (Architect → Coder → Reviewer).
- `run_test_script()`: Triggers a background `pytest` run with HTML report generation and video recording enabled.
- `save_test_case()`: Persists raw manual recordings into JSON plans for future AI training or playback.
- `KnowledgeBrain.add_knowledge()`: Persists patterns and snippets into the ChromaDB vector store.

### Frontend (TSX)
- `startRecording`: Communicates with backend to initiate the live recorder.
- `generateCode`: Triggers the agentic generation and handles real-time logging display.
- `runTest`: Executes a saved automation script and polls for report availability.
- `Dashboard`: Real-time monitoring component tracking token usage, latency, and AI infrastructure status.

---

## 📁 Storage & Organization
- `backend/`: Core logic, API routes, and AI services.
- `frontend/`: React components and UI code.
- `tests_web/`: Automatically persisted Playwright scripts (`test_*.py`).
- `reports/`: Professional HTML test reports and execution videos.
- `test_plans/`: Structured JSON test cases saved from manual recordings.
- `extension/`: Chrome extension source code for remote browser recording.

---

## 💡 Important for Users
- **Hybrid Fallback**: The system automatically switches to your local AI (standardly via Ollama) if your daily cloud token quota is exceeded or if cloud latency is too high (>15s).
- **Self-Healing**: Locators are observed and stored in the **Knowledge Hub**. If a UI change breaks a selector, the AI uses RAG to "heal" the script by looking up past stable attributes.
- **Auth Persistence**: Cloud AI uses your local Qwen OAuth credentials (`oauth_creds.json`) for seamless authentication.
