"""
Knowledge Brain Service
Manages knowledge base imported from AnythingLLM and other sources.
Provides tag-based training and smart matching for test generation.
"""

import json
import os
from pathlib import Path
from typing import Any, List, Dict, Optional
from datetime import datetime
import hashlib
import asyncio
import logging

logger = logging.getLogger(__name__)

def _get_knowledge_service():
    """Helper to avoid early import issues."""
    try:
        from services.knowledge_service import get_knowledge_service
        return get_knowledge_service()
    except ImportError:
        from .services.knowledge_service import get_knowledge_service
        return get_knowledge_service()


class KnowledgeBrain:
    """Knowledge Brain for storing and querying training data."""

    def __init__(self, storage_path: str = None):
        if storage_path is None:
            # Backend storage location
            # Backend storage location (relative to core)
            base_path = Path(__file__).parent.parent
            storage_path = base_path / "storage" / "knowledge"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.knowledge_file = self.storage_path / "knowledge.json"
        self.tags_file = self.storage_path / "tags.json"

        # Initialize storage files
        if not self.knowledge_file.exists():
            self._save_json(self.knowledge_file, {"documents": [], "chunks": []})
        if not self.tags_file.exists():
            self._save_json(self.tags_file, self._default_tags())

    def _default_tags(self) -> dict:
        """Default tag categories for test generation."""
        return {
            "test_types": {
                "positive": ["valid_login", "happy_path", "success"],
                "negative": ["wrong_password", "invalid_data", "error_case"],
                "edge": ["long_string", "boundary", "max_length"],
                "ui": ["screenshot", "layout", "responsive"],
                "api": ["endpoint", "status_code", "authentication"]
            },
            "features": {
                "login": ["authentication", "password", "session"],
                "employee": ["profile", "information", "details"],
                "attendance": ["check_in", "check_out", "shift"]
            }
        }

    def _load_json(self, filepath: Path) -> dict:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_json(self, filepath: Path, data: dict):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _auto_tag(self, content: str) -> list:
        content_lower = content.lower()
        tags = []
        if any(kw in content_lower for kw in ["login", "password", "authenticate"]):
            tags.append("authentication")
        if any(kw in content_lower for kw in ["error", "fail", "invalid"]):
            tags.append("negative")
        return list(set(tags))

    async def add_knowledge(
        self, content: str, title: str, tags: list = None, source: str = "manual"
    ) -> dict:
        """Add new knowledge entry."""
        knowledge = self._load_json(self.knowledge_file)

        chunk_id = hashlib.md5(content.encode()).hexdigest()[:12]
        doc_id = f"manual_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        chunk = {
            "id": f"manual_{chunk_id}",
            "document_id": doc_id,
            "title": title,
            "content": content,
            "tags": tags or self._auto_tag(content),
            "source": source,
            "created_at": datetime.now().isoformat(),
        }

        knowledge["chunks"].append(chunk)
        self._save_json(self.knowledge_file, knowledge)

        # Add to vector store for semantic search
        await _get_knowledge_service().add_document(
            content=content,
            source=source,
            tags=chunk["tags"],
            metadata={
                "document_id": doc_id,
                "chunk_id": chunk["id"],
                "title": title
            }
        )

        return {"success": True, "chunk_id": chunk["id"]}

    async def query(self, query_text: str, limit: int = 10) -> list:
        """Query knowledge base using Semantic Search."""
        try:
            service = _get_knowledge_service()
            semantic_results = await service.search_knowledge(query_text, limit=limit)
            
            formatted = []
            for res in semantic_results:
                formatted.append({
                    "id": res.get("id"),
                    "title": res.get("metadata", {}).get("title", "Reference"),
                    "content": res.get("content", ""),
                    "tags": res.get("metadata", {}).get("tags", "").split(",") if res.get("metadata",{}).get("tags") else [],
                    "score": res.get("score", 0.5)
                })
            return formatted
        except Exception as e:
            logger.error(f"Knowledge query failed: {e}")
            return []

    def get_brain_stats(self) -> dict:
        """Get knowledge base statistics."""
        knowledge = self._load_json(self.knowledge_file)
        chunks = knowledge.get("chunks", [])
        
        tag_counts = {}
        for chunk in chunks:
            for tag in chunk.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
                
        return {
            "total_documents": len(set(c.get("document_id") for c in chunks)),
            "total_chunks": len(chunks),
            "tag_distribution": tag_counts,
            "available_test_types": list(self._default_tags()["test_types"].keys())
        }

# Singleton
_knowledge_brain = None

def get_knowledge_brain() -> KnowledgeBrain:
    global _knowledge_brain
    if _knowledge_brain is None:
        _knowledge_brain = KnowledgeBrain()
    return _knowledge_brain
