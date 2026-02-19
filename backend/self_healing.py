from agentic_service import VisualInspectorTool
from hybrid_pipeline import pipeline
from typing import Optional

class SelfHealer:
    def __init__(self, page):
        self.page = page
        self.inspector = VisualInspectorTool(page)

    async def heal_selector(self, broken_selector: str, expected_description: str) -> Optional[str]:
        """
        Uses AI Vision to find a new selector if the original one fails.
        """
        print(f"🔧 Attempting self-healing for: {broken_selector}")
        
        # 1. Capture visual context
        vision_report = await self.inspector.forward(f"I was looking for '{expected_description}' but '{broken_selector}' is gone. Find the new element.")
        
        # 2. Use Hybrid Pipeline to determine the new selector from vision report
        prompt = (
            f"The original CSS selector '{broken_selector}' failed.\n"
            f"AI Vision Report: {vision_report}\n"
            "Suggest a new, stable CSS selector for this element."
        )
        
        new_selector = await pipeline.route_query(prompt, task_type="complex_healing")
        return new_selector if "error" not in new_selector.lower() else None

healer = None # Initialized per page session
