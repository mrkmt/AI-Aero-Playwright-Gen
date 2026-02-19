from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from dotenv import load_dotenv
from burmese_router import router as burmese_router
from recorder_router import router as recorder_router

load_dotenv()

app = FastAPI(title="AI-Aero-Playwright-Gen", version="1.0.0")

# Ensure reports directory exists
backend_dir = Path(__file__).parent
reports_dir = backend_dir.parent / "reports"
reports_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/reports", StaticFiles(directory=str(reports_dir)), name="reports")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(burmese_router)
app.include_router(recorder_router)

@app.get("/")
async def root():
    return {"message": "AI-Aero-Playwright-Gen API is running locally", "status": "healthy"}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
