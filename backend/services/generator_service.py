import os
from datetime import datetime
from pathlib import Path
import uuid
import re
from typing import List, Dict, Any, Tuple
from core.hybrid_pipeline import pipeline
from core.knowledge_brain import get_knowledge_brain
from services.activity_service import activity_service

SYSTEM_PROMPT = """
You are an expert Playwright automation engineer specialized in JavaScript-heavy Enterprise Apps.
The target system uses:
- Framework: Angular (Zone.js)
- UI: Bootstrap
- Components: TinyMCE (Rich Text), Chart.js, jQuery, Chatwoot
- Language: TypeScript

Your task is to convert recorded steps into a professional Python Playwright script using the pytest-playwright pattern.
Follow these guidelines:
1. Use `pytest` style functions (e.g., `def test_recorded_flow(page: Page):`).
2. Use the `page` fixture.
3. **STRUCTURED HEADER**: Every test function MUST have a docstring with:
   - summary: <Brief description>
   - steps: <Numbered steps>
   - data: <Input values used>
   - expected: <What should happen>
4. **SELECTOR STABILITY**: Prefer `page.get_by_label`, `page.get_by_placeholder`, or `page.get_by_role`. For Angular apps, be wary of dynamic IDs.
5. **RICH TEXT (TinyMCE)**: If interacting with rich text, use iframe selectors or `page.evaluate`.
6. **Negative Testing**: If the instruction asks for a Negative Test, simulate incorrect inputs and ASSERT on error messages.
7. Return ONLY the code, no markdown formatting.
8. **CRITICAL PYTHON SYNTAX**: In Playwright Python, `.first` and `.last` are PROPERTIES. Use `locator.first`, NOT `locator.first()`.
"""

async def generate_playwright_code(steps: List[Dict[str, Any]], url: str, test_type: str = "Normal") -> Tuple[str, str]:
    """
    Generates Playwright Python code and saves it to a file.
    Returns: (generated_code, saved_file_path)
    """
    # Format steps for the LLM
    steps_text = f"Target URL: {url}\n\nSteps:\n"
    for i, step in enumerate(steps):
        action = step.get('action_type', 'unknown')
        selector = step.get('selector_snapshot', 'unknown')
        value = step.get('input_value_masked', '')
        steps_text += f"{i+1}. {action} on '{selector}'"
        if value:
            steps_text += f" with value '{value}'"
        steps_text += "\n"

    try:
        # from services.activity_service import activity_service # Moved to top
        # --- AGENT A: ARCHITECT ---
        print("🕵️ Agent A (Architect) is planning the test structure...")
        activity_service.add_log(f"Architect is planning the test structure (Type: {test_type})...", agent="ARCHITECT")
        planner_prompt = f"""
Given these manual steps, create a logical test plan and outline for a Playwright script.
Test Type Instruction: {test_type}

Recorded Steps:
{steps_text}

If Test Type is 'Negative', plan to simulate incorrect credential entry or intentional failure points and verify error messages.
If Test Type is 'Sanity', focus on the most critical path.
"""
        plan = await pipeline.generate_with_fallback(planner_prompt, system_prompt="You are Agent A, a Test Architect. Create a pseudo-code plan.", agent_name="ARCHITECT")

        # --- AGENT B: CODER ---
        print("💻 Agent B (Coder) is implementing the Playwright script...")
        activity_service.add_log("Coder is implementing the Playwright script...", agent="CODER")
        coder_prompt = f"Using this plan: {plan}\n\nImplement the full Playwright Python script for these steps:\n{steps_text}"
        raw_code = await pipeline.generate_with_fallback(coder_prompt, system_prompt=SYSTEM_PROMPT, agent_name="CODER")

        # --- AGENT C: REVIEWER ---
        print("🔍 Agent C (Reviewer) is validating the script...")
        activity_service.add_log("Reviewer is validating the script...", agent="REVIEWER")
        reviewer_prompt = f"Review this Playwright script for any errors, missing waits, or unstable selectors. Fix it if necessary and return the final clean code:\n{raw_code}"
        final_code = await pipeline.generate_with_fallback(reviewer_prompt, system_prompt="You are Agent C, a Senior Automation Engineer. Output ONLY the final polished Python code.", agent_name="REVIEWER")

        # Strip markdown code blocks if present
        code = final_code
        if "```" in code:
            parts = code.split("```")
            code = next((p.split("\n", 1)[1] if "\n" in p else p for p in parts if p.strip().startswith(("python", "py", ""))), code)
            if "```" in code:
                code = code.split("```")[0]

        code = code.strip()

        # --- KNOWLEDGE INTEGRATION: SELF-HEALING ---
        try:
            brain = get_knowledge_brain()
            locators = []
            for step in steps:
                if step.get("selector_snapshot"):
                    locators.append(step["selector_snapshot"])
            
            if locators:
                activity_service.add_log(f"Persisting {len(locators)} locators to Knowledge Hub for self-healing...", agent="SYSTEM")
                brain.add_knowledge(
                    title=f"Locators for {url}",
                    content=f"Site URL: {url}\nObserved Locators: {', '.join(locators)}",
                    tags=["locators", "self-healing", url]
                )
        except Exception as ke:
            print(f"⚠️ Knowledge save failed: {ke}")

        # --- PERSISTENCE ---
        filename = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        # Adjusted for the user's project structure
        backend_dir = Path(__file__).parent.parent
        save_dir = backend_dir.parent / "tests_web"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        file_path = os.path.join(save_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        print(f"✅ Script saved to: {file_path}")
        
        # --- KNOWLEDGE BRAIN INTEGRATION ---
        try:
            from core.knowledge_brain import get_knowledge_brain
            kb = get_knowledge_brain()
            # Feed the generated code into the knowledge base for future RAG optimization
            import asyncio
            asyncio.create_task(kb.add_knowledge(
                content=code,
                title=f"Autogen Playwright: {filename}",
                tags=["playwright", "autogen", "success"],
                source="generator_service"
            ))
            print("🧠 Knowledge Brain updated with new automation pattern.")
        except Exception as kb_err:
            print(f"⚠️ Knowledge Brain update failed: {kb_err}")

        return code, file_path

    except Exception as e:
        error_msg = f"# Error in Agentic Orchestration: {str(e)}\n# Please ensure the AI services are reachable."
        return error_msg, ""
