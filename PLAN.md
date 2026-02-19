# AI-Aero Playwright Generator: Team Project Plan 🚀

This project is an **AI-powered automation factory**. It records manual browser actions and uses advanced AI "Agents" to write high-quality, stable Playwright test scripts automatically.

## 🛠 Core Frameworks & Tools
Our system is built on a "Full-Stack Automation" stack:

*   **Automation Framework**: [Playwright](https://playwright.dev/) (Python) - The primary engine for browser execution.
*   **Web API (Backend)**: [FastAPI](https://fastapi.tiangolo.com/) - High-performance asynchronous Python backend.
*   **Interface (Frontend)**: [React](https://reactjs.org/) + [Vite](https://vitejs.dev/) - Modern, fast UI with [Tailwind CSS](https://tailwindcss.com/) for styling.
*   **Bridge (Extension)**: Chrome Manifest V3 - A custom-built injector for real-time event capturing.
*   **AI Router**: [LiteLLM](https://github.com/BerriAI/litellm) - Standardized interface to call any LLM provider (Cloud/Local).

## 🧠 AI Models & Infrastructure
We use a "Hybrid Brain" approach to balance cost, speed, and privacy.

| Category | Model Name | Role | Provider |
| :--- | :--- | :--- | :--- |
| **Cloud Primary** | `qwen-max` | High-complexity logic & Reviewer agent | Alibaba Qwen |
| **Local Fallback** | `llama3.2:3b` | Quick generation & data privacy | [Ollama](https://ollama.com/) |
| **Vision Model** | `moondream` | UI analysis & selector healing | Ollama |

### Authentication Modes
1.  **OAuth 2.0**: Direct integration with Qwen's global auth system (no static API keys).
2.  **OpenClaw Gateway**: Optional proxy for enterprise-grade AI orchestration and logging.

---

## 🔄 Core Workflow
How a team member uses this system:
1.  **Capture**: Use the Chrome Extension to record a manual test on any website.
2.  **Verify**: Open the **Aero Dashboard** to see the recorded steps in real-time.
3.  **Generate**: Click "Generate Code." Three AI Agents collaborate:
    *   **Agent A (Planner)**: Designs the test path.
    *   **Agent B (Coder)**: Writes the actual Python code.
    *   **Agent C (Reviewer)**: Fixes any small bugs or timing issues.
4.  **Monitor**: Use the **System Monitor** tab to check token usage and AI health.

---

## � How to Run the Project
To start working on the project, follow these two steps in separate terminals:

### 1. Run the Backend (The Brain)
Open a terminal in the `backend` folder and run:
```powershell
# 1. Enter the folder
cd backend

# 2. Activate the virtual environment
.\venv\Scripts\activate

# 3. Start the server
uvicorn main:app --reload
```
*Note: The backend will be available at [http://localhost:8000](http://localhost:8000)*

### 2. Run the Frontend (The Dashboard)
Open a second terminal in the `frontend` folder and run:
```powershell
# 1. Enter the folder
cd frontend

# 2. Start the development server
npm run dev
```
*Note: The dashboard will be available at [http://localhost:5173](http://localhost:5173)*

---

## �📍 Current Progress: Phase 1 (Completed)
We have successfully finished the core foundation:
- [x] **Unified AI Bridge**: Connects to Qwen Cloud (via OAuth) and Local Ollama automatically.
- [x] **Smart Fallback**: If Cloud is slow or over-quota, it automatically uses Local AI.
- [x] **Agentic Logic**: The "Planner-Coder-Reviewer" chain is live for better code quality.
- [x] **Monitoring Dashboard**: Real-time tracking of tokens and response speeds.
- [x] **Extension Sync**: Data flows perfectly from the browser to the backend.

---

## ⏭ Next Steps (Phase 2 & Beyond)
- **Visual Validation**: Integrating the "Vision Lab" for AI-powered UI checks.
- **Test Variations**: Automatically generating 10+ edge cases for every 1 recording.
- **CI/CD Integration**: One-click export to GitHub Actions or Jenkins.

**Ready to start?** Just run the backend, open the dashboard, and start recording! 🦾
