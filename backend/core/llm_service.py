"""
LLM Service Adapter
Bridges the ported ai-k-os logic with the existing HybridAIPipeline.
"""

import logging
from typing import List, Optional, Any
import os

from .hybrid_pipeline import pipeline

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with LLM via HybridAIPipeline"""

    def __init__(self):
        self.pipeline = pipeline
        logger.info("LLMService (Adapter) initialized")

    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        images: Optional[List[str]] = None,
    ) -> str:
        """
        Generate response using HybridAIPipeline.
        Temperature and images are currently ignored by the base pipeline but can be added if needed.
        """
        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\nUser Question:\n{prompt}"
            
        # We can map 'model' to a specific agent if needed, or just use general fallback
        # For Telegram bot, let's use 'CODER' or 'ARCHITECT' profile if available
        return await self.pipeline.generate_with_fallback(
            prompt=full_prompt,
            system_prompt=system_prompt,
            agent_name="CODER" # Default to Coder for general questions
        )

# Global instance
_llm_service: Optional[LLMService] = None

def get_llm_service() -> LLMService:
    """Get or create global LLMService instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
