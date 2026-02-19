from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import asyncio
from burmese_engine import PlaywrightRunner

router = APIRouter(prefix="/api/v1/burmese", tags=["burmese"])

class BurmeseCommandRequest(BaseModel):
    script: str  # The Burmese script text
    url: Optional[str] = None

class BurmeseCommandResponse(BaseModel):
    status: str
    message: str
    artifacts: List[str] = []

@router.post("/execute", response_model=BurmeseCommandResponse)
async def execute_burmese_script(request: BurmeseCommandRequest):
    """
    Executes a natural language script in Burmese.
    Example: 'ဖွင့် https://google.com'
    """
    try:
        # Here we would initialize the ported runner
        # For now, we simulate the execution logic from burmese_engine.py
        runner = PlaywrightRunner() 
        success, msg = await runner.run_script(request.script)
        
        if not success:
            raise HTTPException(status_code=400, detail=msg)
            
        return BurmeseCommandResponse(
            status="success",
            message=msg,
            artifacts=["screenshot_latest.png"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
