# AI-K-OS-PREMIUM Architecture

## Overview
The platform is a unified QA command center designed for high-availability and intelligent automation.

## Components

### 1. Unified Frontend (React)
- State management for test runs and records.
- Vision Lab for pixel-perfect visual regression.
- Interactive Command Center dashboard.

### 2. Intelligent Backend (FastAPI)
- **Agentic Service**: Manages self-healing via Smolagents.
- **Knowledge Service**: Connects to AnythingLLM and Vector Stores.
- **Runner Service**: Orchestrates Playwright and Patrol executions.
- **Telegram Gateway**: Facilitates remote control via OpenClaw.

### 3. Data Layer
- **PostgreSQL**: Primary data store for test results, users, and settings.
- **ChromaDB/pgvector**: Vector storage for semantic search and context.
- **SQLite**: Fast local caching for ephemeral session data.

## Data Flow
1. **Trigger**: User starts a run (Web UI or Telegram).
2. **Planning**: AI Planner fetches context from Knowledge Store.
3. **Execution**: Runner executes Playwright specs.
4. **Heal**: If failures occur, the Healer Agent attempts a fix.
5. **Store**: Results are saved to Postgres and logs are archived.
6. **Notify**: Final report sent via OpenClaw to the user.

---
*Created by Antigravity AI*
