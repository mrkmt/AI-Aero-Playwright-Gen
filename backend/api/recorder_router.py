from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from services.recorder_service import start_recording, stop_recording, session_steps, handle_extension_message
from services.telegram_bot import get_telegram_bot
from core.knowledge_brain import get_knowledge_brain
from services.activity_service import activity_service

router = APIRouter(prefix="/api/v1/recorder", tags=["recorder"])

class SessionStartRequest(BaseModel):
    url: str
    session_name: str = "default"

class RunTestRequest(BaseModel):
    headless: bool = False
    test_type: str = "Normal" # Normal, Negative, Sanity

class RecordStepRequest(BaseModel):
    session_id: str
    action: str
    selector: str
    value: str = ""

class ExtensionStepsRequest(BaseModel):
    steps: List[Dict[str, Any]]

class AgentProfilesUpdate(BaseModel):
    profiles: List[Dict[str, Any]]
    assignments: Dict[str, str]
    gateway: Dict[str, str] = {"url": "", "token": ""}

@router.post("/start")
async def start_session(request: SessionStartRequest):
    # Recording is ALWAYS headed (visual) as requested by user
    result = start_recording(request.session_name, request.url, headless=False)
    activity_service.add_log(f"Started visual recording session: {request.session_name} on {request.url}", agent="Recorder")
    return result

@router.post("/stop/{session_id}")
async def stop_session(session_id: str):
    result = stop_recording(session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    activity_service.add_log(f"Stopped recording session: {session_id}", agent="Recorder")
    return result

@router.get("/{session_id}/steps")
async def get_steps(session_id: str):
    return session_steps(session_id)

@router.post("/recording/steps")
async def receive_extension_steps(request: ExtensionStepsRequest, session_id: str = "default"):
    """Endpoint for the Chrome extension to POST recorded steps."""
    for step in request.steps:
        handle_extension_message(session_id, step)
    return {"status": "received", "count": len(request.steps)}

@router.post("/custom-code")
async def generate_code(request: ExtensionStepsRequest, url: str, test_type: str = "Normal"):
    from services.generator_service import generate_playwright_code
    code, file_path = await generate_playwright_code(request.steps, url, test_type=test_type)
    return {"code": code, "file_path": file_path}

@router.get("/usage")
async def get_usage():
    from core.hybrid_pipeline import pipeline
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
    # Get project root (one level up from backend)
    project_root = Path(__file__).parent.parent.parent
    save_dir = project_root / "tests_web"
    if not os.path.exists(save_dir):
        return {"scripts": []}
    
    files = [f for f in os.listdir(save_dir) if f.endswith(".py")]
    # Sort by descending order (newest first)
    files.sort(reverse=True)
    return {"scripts": files}

@router.post("/run/{filename}")
async def run_test_script(filename: str, request: RunTestRequest):
    import subprocess
    import os
    
    # Get project root
    project_root = Path(__file__).parent.parent.parent
    tests_dir = project_root / "tests_web"
    reports_dir = project_root / "reports"
    script_path = os.path.join(tests_dir, filename)
    
    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail="Test script not found")
        
    report_name = f"report_{filename.replace('.py', '')}_{datetime.now().strftime('%H%M%S')}.html"
    report_path = os.path.join(reports_dir, report_name)
    
    # Run pytest in a background process
    # Note: Using path relative to backend dir for venv
    backend_dir = Path(__file__).parent.parent
    python_exe = backend_dir / "venv" / "Scripts" / "python.exe"
    if not python_exe.exists():
        # Fallback for non-windows or different structure
        python_exe = "python"
        
    cmd = [
        str(python_exe), "-m", "pytest",
        script_path,
        f"--html={report_path}",
        "--self-contained-html",
        "--video", "on",
        f"--headless={str(request.headless).lower()}", # Note: Requires pytest-playwright to handle this or we pass as env
        "-v"
    ]
    
    activity_service.add_log(f"Running test {filename} (Type: {request.test_type}, Headless: {request.headless})", agent="SYSTEM")
    
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
    project_root = Path(__file__).parent.parent.parent
    reports_dir = project_root / "reports"
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

@router.get("/profiles")
async def get_profiles():
    import json
    import os
    # Adjusted to follow the current directory structure (backend/api/recorder_router.py)
    profiles_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agent_profiles.json")
    if not os.path.exists(profiles_path):
        return {"profiles": [], "assignments": {}}
    with open(profiles_path, "r") as f:
        return json.load(f)

@router.get("/activity")
async def get_activity():
    return {"logs": activity_service.get_logs()}
    
@router.post("/profiles")
async def update_profiles(data: AgentProfilesUpdate):
    import json
    import os
    profiles_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agent_profiles.json")
    try:
        with open(profiles_path, "w") as f:
            json.dump(data.dict(), f, indent=2)
            
        # Dynamically update bot settings
        from services.telegram_bot import get_telegram_bot
        bot = get_telegram_bot()
        if data.gateway:
            bot.bot_token = data.gateway.get("token", bot.bot_token)
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Telegram & Knowledge Base Integration ---

@router.post("/telegram/webhook")
async def telegram_webhook(update: Dict[str, Any], x_telegram_secret: Optional[str] = Header(None, alias="X-Telegram-Bot-Api-Secret-Token")):
    """
    Direct Telegram Webhook for Aero Gateway.
    Verifies secret and processes messages.
    """
    bot = get_telegram_bot()
    
    # Verify secret if configured
    if bot.webhook_secret and x_telegram_secret != bot.webhook_secret:
        return JSONResponse(status_code=401, content={"error": "Unauthorized Gateway Access"})
    
    # Normalize Telegram's nested structure to a flat format the bot expects
    # Telegram sends: {"update_id": ..., "message": {"chat": {"id": ...}, "text": "...", ...}}
    if "message" in update:
        msg = update["message"]
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "")
        formatted_msg = {
            "chat_id": str(chat_id),
            "user_id": str(msg.get("from", {}).get("id", chat_id)),
            "text": text,
            "message_id": msg.get("message_id")
        }
        result = await bot.handle_message(formatted_msg)
        return result
        
    return {"status": "ignored"}

# --- Test Plan & Case Management ---

@router.post("/plans/save")
async def save_test_case(request: Dict[str, Any]):
    import json
    import os
    plan_name = request.get("plan_name", "DefaultPlan").strip() or "DefaultPlan"
    case_name = request.get("case_name", "UntitledCase").strip() or "UntitledCase"
    steps = request.get("steps", [])
    
    # Target directory: backend/test_plans/{plan_name}
    base_dir = os.path.dirname(os.path.dirname(__file__))
    plans_dir = os.path.join(base_dir, "test_plans", plan_name)
    os.makedirs(plans_dir, exist_ok=True)
    
    file_path = os.path.join(plans_dir, f"{case_name}.json")
    with open(file_path, "w") as f:
        json.dump({
            "plan_name": plan_name,
            "case_name": case_name,
            "steps": steps,
            "updated_at": datetime.now().isoformat()
        }, f, indent=2)
    
    activity_service.add_log(f"Saved Test Case '{case_name}' to Plan '{plan_name}'", agent="SYSTEM")
    return {"status": "success", "path": file_path}

@router.get("/plans")
async def list_test_plans():
    import os
    base_dir = os.path.dirname(os.path.dirname(__file__))
    plans_root = os.path.join(base_dir, "test_plans")
    if not os.path.exists(plans_root):
        return {"plans": []}
    
    plans = []
    for plan_name in os.listdir(plans_root):
        plan_path = os.path.join(plans_root, plan_name)
        if os.path.isdir(plan_path):
            cases = [f.replace(".json", "") for f in os.listdir(plan_path) if f.endswith(".json")]
            plans.append({"name": plan_name, "cases": cases})
    
    return {"plans": plans}

@router.get("/plans/{plan_name}/{case_name}")
async def get_test_case(plan_name: str, case_name: str):
    import json
    import os
    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "test_plans", plan_name, f"{case_name}.json")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Test case not found")
        
    with open(file_path, "r") as f:
        return json.load(f)

@router.get("/knowledge/search")
# ... existing
async def search_knowledge(query: str, limit: int = 5):
    kb = get_knowledge_brain()
    results = await kb.query(query, limit=limit)
    return {"results": results}

@router.get("/knowledge/stats")
async def get_knowledge_stats():
    kb = get_knowledge_brain()
    return kb.get_brain_stats()

@router.post("/knowledge/train")
async def manual_train(request: Dict[str, Any]):
    kb = get_knowledge_brain()
    result = await kb.add_knowledge(
        content=request.get("content", ""),
        title=request.get("title", "Manual Training"),
        tags=request.get("tags", []),
        source="ui"
    )
    return result
