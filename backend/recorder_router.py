from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from recorder_service import start_recording, stop_recording, session_steps, handle_extension_message

router = APIRouter(prefix="/api/v1/recorder", tags=["recorder"])

class SessionStartRequest(BaseModel):
    url: str
    session_name: str = "default"

class RecordStepRequest(BaseModel):
    session_id: str
    action: str
    selector: str
    value: str = ""

class ExtensionStepsRequest(BaseModel):
    steps: List[Dict[str, Any]]

@router.post("/start")
async def start_session(request: SessionStartRequest):
    result = start_recording(request.session_name, request.url)
    return result

@router.post("/stop/{session_id}")
async def stop_session(session_id: str):
    result = stop_recording(session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return result

@router.get("/{session_id}/steps")
async def get_steps(session_id: str):
    steps = session_steps(session_id)
    return {"steps": steps}

@router.post("/recording/steps")
async def receive_extension_steps(request: ExtensionStepsRequest):
    """Endpoint for the Chrome extension to POST recorded steps."""
    return {"status": "received", "count": len(request.steps)}

@router.post("/custom-code")
async def generate_code(request: ExtensionStepsRequest, url: str):
    from generator_service import generate_playwright_code
    code, file_path = await generate_playwright_code(request.steps, url)
    return {"code": code, "file_path": file_path}

@router.get("/usage")
async def get_usage():
    from hybrid_pipeline import pipeline
    usage = pipeline._get_usage()
    return {
        "usage": usage,
        "limits": {
            "daily_quota": pipeline.daily_quota,
            "latency_threshold": pipeline.latency_threshold,
            "cloud_model": pipeline.cloud_model,
            "local_model": pipeline.local_model
        }
    }
@router.get("/saved-scripts")
async def list_saved_scripts():
    import os
    save_dir = r"D:\KMT\My class\AI\AI-Aero-Playwright-Gen\tests_web"
    if not os.path.exists(save_dir):
        return {"scripts": []}
    
    files = [f for f in os.listdir(save_dir) if f.endswith(".py")]
    # Sort by descending order (newest first)
    files.sort(reverse=True)
    return {"scripts": files}

@router.post("/run/{filename}")
async def run_test_script(filename: str):
    import subprocess
    import os
    from datetime import datetime
    
    tests_dir = r"D:\KMT\My class\AI\AI-Aero-Playwright-Gen\tests_web"
    reports_dir = r"D:\KMT\My class\AI\AI-Aero-Playwright-Gen\reports"
    script_path = os.path.join(tests_dir, filename)
    
    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail="Test script not found")
        
    report_name = f"report_{filename.replace('.py', '')}_{datetime.now().strftime('%H%M%S')}.html"
    report_path = os.path.join(reports_dir, report_name)
    
    # Run pytest in a background process
    # Note: Using absolute path to venv python for stability
    python_exe = r"D:\KMT\My class\AI\AI-Aero-Playwright-Gen\backend\venv\Scripts\python.exe"
    cmd = [
        python_exe, "-m", "pytest",
        script_path,
        f"--html={report_path}",
        "--self-contained-html",
        "-v"
    ]
    
    try:
        # For this implementation, we run it and wait (simplified for now)
        # In a real heavy app, this would be an async task queue (Celery/RQ)
        subprocess.Popen(cmd)
        return {"status": "started", "report_url": f"/reports/{report_name}", "report_name": report_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def list_reports():
    import os
    reports_dir = r"D:\KMT\My class\AI\AI-Aero-Playwright-Gen\reports"
    if not os.path.exists(reports_dir):
        return {"reports": []}
    
    files = []
    for f in os.listdir(reports_dir):
        if f.endswith(".html"):
            stats = os.stat(os.path.join(reports_dir, f))
            files.append({
                "name": f,
                "url": f"http://localhost:8000/reports/{f}",
                "timestamp": stats.st_mtime
            })
    
    # Sort by descending time
    files.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"reports": files}
