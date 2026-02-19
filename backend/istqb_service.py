from typing import List, Dict, Any
from templates import QA_TEMPLATES
from hybrid_pipeline import pipeline

class ISTQBGenerator:
    def __init__(self):
        self.standard_template = QA_TEMPLATES.get("standard_qa", "")

    async def generate_test_case(self, requirements: str, format: str = "standard_qa") -> str:
        """
        Generates a professional test case using ISTQB standards.
        """
        template = QA_TEMPLATES.get(format, self.standard_template)
        
        prompt = (
            f"As a Senior QA Engineer following ISTQB standards, generate a comprehensive test case for:\n"
            f"Requirements: {requirements}\n\n"
            f"Follow this template:\n{template}\n\n"
            f"Include Priority, Risk Level, and Preconditions."
        )
        
        # Use Hybrid Pipeline for high-quality generation
        return await pipeline.route_query(prompt, task_type="generation")

generator = ISTQBGenerator()
