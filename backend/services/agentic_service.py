import logging
import json
import base64
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lightweight stubs replacing the missing app.config / app.services modules
# ---------------------------------------------------------------------------


@dataclass
class _Settings:
    ai_heal_enabled: bool = os.getenv("AI_HEAL_ENABLED", "True").lower() == "true"
    vision_model: str = os.getenv("AI_LOCAL_MODEL", "llama3.2:3b")
    api_base: str = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")


settings = _Settings()


def get_llm_service():
    """Stub — returns None. Full LLM service requires the ai-k-os app package."""
    return None


# ---------------------------------------------------------------------------
# Tools (usable when Playwright page + smolagents are available)
# ---------------------------------------------------------------------------

try:
    from smolagents import CodeAgent, Tool, LiteLLMModel

    _SMOLAGENTS_AVAILABLE = True
except ImportError:
    _SMOLAGENTS_AVAILABLE = False

    # Define a minimal Tool base so the file can still be imported
    class Tool:  # type: ignore[no-redef]
        name = ""
        description = ""
        inputs: dict = {}
        output_type = "string"

        def __init__(self, **kw):
            pass

        def forward(self, *a, **kw):
            return ""


class VisualInspectorTool(Tool):
    name = "inspect_visually"
    description = "Captures a screenshot and uses AI Vision to describe the UI or find specific elements."
    inputs = {
        "requirement": {
            "type": "string",
            "description": "What to look for in the screenshot.",
        }
    }
    output_type = "string"

    def __init__(self, page, **kwargs):
        super().__init__(**kwargs)
        self.page = page

    def forward(self, requirement: str) -> str:
        try:
            screenshot_bytes = self.page.screenshot(type="jpeg", quality=50)
            b64_image = base64.b64encode(screenshot_bytes).decode("utf-8")
            return f"[Visual inspection placeholder — {len(b64_image)} bytes captured]"
        except Exception as e:
            return f"Error during visual inspection: {str(e)}"


class DomInspectorTool(Tool):
    name = "inspect_dom"
    description = "Inspects the current page DOM and returns a condensed version of the HTML structure."
    inputs = {
        "query": {
            "type": "string",
            "description": "Optional search term to filter elements.",
            "nullable": True,
        }
    }
    output_type = "string"

    def __init__(self, page, **kwargs):
        super().__init__(**kwargs)
        self.page = page

    def forward(self, query: Optional[str] = None) -> str:
        try:
            script = """
            (query) => {
                const elements = document.querySelectorAll(query || 'button, input, a, [role="button"], span');
                const results = [];
                elements.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        results.push({
                            tag: el.tagName,
                            id: el.id,
                            class: el.className,
                            text: el.innerText.trim().substring(0, 50),
                            name: el.getAttribute('name'),
                            placeholder: el.getAttribute('placeholder'),
                            ariaLabel: el.getAttribute('aria-label')
                        });
                    }
                });
                return JSON.stringify(results.slice(0, 30));
            }
            """
            return self.page.evaluate(script, query)
        except Exception as e:
            return f"Error inspecting DOM: {str(e)}"


class SelectorValidatorTool(Tool):
    name = "validate_selector"
    description = "Validates if a CSS selector exists on the page and returns how many elements it matches."
    inputs = {
        "selector": {"type": "string", "description": "The CSS selector to validate."}
    }
    output_type = "string"

    def __init__(self, page, **kwargs):
        super().__init__(**kwargs)
        self.page = page

    def forward(self, selector: str) -> str:
        try:
            count = self.page.locator(selector).count()
            if count == 0:
                return f"Selector '{selector}' matches NO elements."
            elif count == 1:
                return f"Selector '{selector}' is UNIQUE and matches 1 element."
            else:
                return (
                    f"Selector '{selector}' is NOT unique. It matches {count} elements."
                )
        except Exception as e:
            return f"Error validating selector: {str(e)}"


async def agentic_heal_selector(
    page: Any, failing_selector: str, description: str, object_id: Optional[str] = None
) -> Optional[str]:
    """
    Uses Smolagents to find a replacement for a failing selector on the current page.
    """
    if not settings.ai_heal_enabled:
        return None

    if not _SMOLAGENTS_AVAILABLE:
        logger.warning("smolagents is not installed — agentic healing unavailable")
        return None

    logger.info(f"Triggering Agentic Healing for: {failing_selector} ({description})")

    try:
        model = LiteLLMModel(
            model_id=f"ollama/{settings.vision_model}",
            api_base=settings.api_base,
            api_key="ollama",
        )
        tools = [
            DomInspectorTool(page),
            SelectorValidatorTool(page),
            VisualInspectorTool(page),
        ]
        agent = CodeAgent(tools=tools, model=model, add_base_tools=False)

        prompt = (
            f"The test step failed because the selector '{failing_selector}' could not be found.\n"
            f"The intended action was: {description}\n\n"
            "Your task:\n"
            "1. Inspect the page DOM using 'inspect_dom'.\n"
            "2. Formulate a robust CSS selector that uniquely identifies the target element.\n"
            "3. Validate the selector using 'validate_selector'.\n"
            "4. Return the new selector as your final answer."
        )

        result = agent.run(prompt)
        logger.info(f"Agentic Healing result: {result}")
        return str(result)
    except Exception as e:
        logger.error(f"Agentic Healing failed: {e}")
        return None
