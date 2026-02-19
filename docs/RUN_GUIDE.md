# 🚀 AI-Aero Playwright Generator: Run Guide

This guide provides step-by-step instructions to get the project up and running on a local machine.

## 📋 Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **Browser**: Google Chrome (for the recorder extension)
- **Local AI (Optional)**: [Ollama](https://ollama.com/) for local model support.

---

## 🛠 Step 1: Backend Setup (Python)
The backend manages the AI logic, agentic workflows, and recording storage.

1.  **Open a Terminal** in the `backend` directory.
2.  **Activate Virtual Environment**:
    ```powershell
    .\venv\Scripts\activate
    ```
3.  **Install Dependencies** (if first time):
    ```powershell
    pip install -r requirements.txt
    ```
4.  **Configure Environment**:
    Ensure the `.env` file exists with your Qwen OAuth path or API keys.
5.  **Run the Server**:
    ```powershell
    uvicorn main:app --reload --port 8000
    ```
    *Access API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)*

---

## 💻 Step 2: Frontend Setup (React)
The frontend provides the Dashboard for managing recordings and generating code.

1.  **Open a Terminal** in the `frontend` directory.
2.  **Install Dependencies** (if first time):
    ```powershell
    npm install
    ```
3.  **Start Dev Server**:
    ```powershell
    npm run dev
    ```
    *Access Dashboard: [http://localhost:5173](http://localhost:5173)*

---

## 🧩 Step 3: Assistant Extension (Chrome)
The extension captures manual browser actions.

1.  Open Chrome and navigate to `chrome://extensions/`.
2.  Enable **Developer Mode** (top-right).
3.  Click **Load unpacked**.
4.  Select the `extension` folder from this project directory.
5.  **Pin the extension** for easy access.

---

## 🔄 Step 4: Normal Workflow
1.  Start both **Backend** and **Frontend**.
2.  Open the Dashboard ([localhost:5173](http://localhost:5173)).
3.  Navigate to **Recorder**, enter a URL, and click **Start Recording**.
4.  Perform actions in the new window.
5.  Stop recording and click **Generate Code**.
6.  Monitor usage in the **Dashboard** tab.
