import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
from hybrid_pipeline import pipeline

SYSTEM_PROMPT = """
You are an expert Playwright automation engineer.
Your task is to convert a list of recorded steps into a professional, robust Python Playwright script using the pytest-playwright pattern.
Follow these guidelines:
1. Use `pytest` style functions (e.g., `def test_recorded_flow(page: Page):`).
2. Do NOT use `sync_playwright()` context managers or manually create browser/context unless absolutely necessary for multi-browser tests.
3. Use the `page` fixture provided by `pytest-playwright`.
4. Add comments explaining each step.
5. Use robust selectors (prefer user-facing attributes like role, name, placeholder).
6. Return ONLY the code, no markdown formatting.
7. Include `from playwright.sync_api import Page, expect` at the top.
"""

async def generate_playwright_code(steps: List[Dict[str, Any]], url: str) -> Tuple[str, str]:
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
        # --- AGENT A: ARCHITECT ---
        print("🕵️ Agent A (Architect) is planning the test structure...")
        planner_prompt = f"Given these manual steps, create a logical test plan and outline for a Playwright script. Focus on Page Object Model components if visible.\n{steps_text}"
        plan = await pipeline.generate_with_fallback(planner_prompt, system_prompt="You are Agent A, a Test Architect. Create a pseudo-code plan.")

        # --- AGENT B: CODER ---
        print("💻 Agent B (Coder) is implementing the Playwright script...")
        coder_prompt = f"Using this plan: {plan}\n\nImplement the full Playwright Python script for these steps:\n{steps_text}"
        raw_code = await pipeline.generate_with_fallback(coder_prompt, system_prompt=SYSTEM_PROMPT)

        # --- AGENT C: REVIEWER ---
        print("🔍 Agent C (Reviewer) is validating the script...")
        reviewer_prompt = f"Review this Playwright script for any errors, missing waits, or unstable selectors. Fix it if necessary and return the final clean code:\n{raw_code}"
        final_code = await pipeline.generate_with_fallback(reviewer_prompt, system_prompt="You are Agent C, a Senior Automation Engineer. Output ONLY the final polished Python code.")

        # Strip markdown code blocks if present
        code = final_code
        if "```" in code:
            parts = code.split("```")
            code = next((p.split("\n", 1)[1] if "\n" in p else p for p in parts if p.strip().startswith(("python", "py", ""))), code)
            if "```" in code:
                code = code.split("```")[0]

        code = code.strip()

        # --- PERSISTENCE ---
        filename = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        # Adjusted for the user's project structure
        save_dir = r"D:\KMT\My class\AI\AI-Aero-Playwright-Gen\tests_web"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        file_path = os.path.join(save_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        print(f"✅ Script saved to: {file_path}")
        return code, file_path

    except Exception as e:
        error_msg = f"# Error in Agentic Orchestration: {str(e)}\n# Please ensure the AI services are reachable."
        return error_msg, ""
