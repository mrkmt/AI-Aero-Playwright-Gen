"""
Knowledge Management Service
Handles document storage, retrieval, and semantic search
With AnythingLLM Integration
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
import httpx
import os

from core.vector_store import get_vector_store
from core.token_manager import get_token_manager

logger = logging.getLogger(__name__)

class KnowledgeService:
    """Service for managing knowledge base operations"""
    
    def __init__(self):
        """Initialize knowledge service"""
        self.vector_store = get_vector_store()
        self.token_manager = get_token_manager()
        
        # Pull from environment variables if available
        self.anythingllm_url = os.getenv("ANYTHINGLLM_URL", "http://localhost:3001")
        self.anythingllm_key = os.getenv("ANYTHINGLLM_API_KEY", "")
        self.workspace_slug = os.getenv("ANYTHINGLLM_WORKSPACE_SLUG", "")
        
        logger.info(f"KnowledgeService initialized. AnythingLLM: {'Enabled' if self.anythingllm_key else 'Disabled'}")
    
    async def add_document(
        self,
        content: str,
        source: str = "manual",
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a document to the knowledge base
        """
        # Count tokens
        token_count = self.token_manager.count_tokens(content)
        
        # Prepare metadata
        doc_metadata = {
            "source": source,
            "tokens": token_count,
            "added_by": user_id or "system",
            "timestamp": datetime.utcnow().isoformat(),
            "tags": ",".join(tags) if tags else ""
        }
        
        if metadata:
            doc_metadata.update(metadata)
        
        # Add to vector store
        doc_id = await self.vector_store.add_document(
            content=content,
            metadata=doc_metadata,
            collection_name="knowledge"
        )
        
        logger.info(f"Added document {doc_id} from {source} to local store")
        
        return {
            "id": doc_id,
            "content": content,
            "metadata": doc_metadata,
            "tokens": token_count
        }
    
    async def search_knowledge(
        self,
        query: str,
        limit: int = 5,
        source_filter: Optional[str] = None,
        tag_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base using AnythingLLM if configured, else local vector store
        """
        # 1. Try AnythingLLM first
        if self.anythingllm_key and self.workspace_slug:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    headers = {"Authorization": f"Bearer {self.anythingllm_key}"}
                    payload = {
                        "message": query,
                        "mode": "query"
                    }
                    
                    response = await client.post(
                        f"{self.anythingllm_url}/api/v1/workspace/{self.workspace_slug}/chat",
                        json=payload,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        text_response = data.get("textResponse", "")
                        sources = data.get("sources", [])
                        
                        results = [{
                            "id": "anythingllm_answer",
                            "content": text_response,
                            "metadata": {"source": "AnythingLLM", "type": "answer"},
                            "score": 1.0
                        }]
                        
                        for src in sources:
                            results.append({
                                "id": src.get("id", "unknown"),
                                "content": src.get("text", "")[:500] + "...",
                                "metadata": {"source": src.get("title", "AnythingLLM Source"), "score": src.get("score")},
                                "score": src.get("score", 0.5)
                            })
                            
                        return results
            except Exception as e:
                logger.error(f"AnythingLLM Connection Error: {e}")
        
        # 2. Local Vector Store Fallback
        filters = {}
        if source_filter:
            filters["source"] = source_filter
        
        # Prepare tag filter if provided
        tag_meta_filter = None
        if tag_filter:
            # ChromaDB $contains logic
            tag_meta_filter = {"tags": {"$contains": tag_filter}}
        
        # Search vector store
        results = await self.vector_store.search_similar(
            query=query,
            collection_name="knowledge",
            limit=limit,
            filter_metadata=tag_meta_filter or (filters if filters else None)
        )
        
        return results
    
    async def add_conversation(
        self,
        conversation_id: str,
        messages: List[Dict[str, str]],
        user_id: str,
        chat_id: str
    ) -> str:
        content = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages
        ])
        
        token_count = self.token_manager.count_tokens(content)
        
        metadata = {
            "source": "telegram",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "chat_id": chat_id,
            "message_count": len(messages),
            "tokens": token_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        doc_id = await self.vector_store.add_document(
            content=content,
            metadata=metadata,
            collection_name="conversations",
            doc_id=conversation_id
        )
        
        logger.info(f"Added conversation {conversation_id}")
        return doc_id

# Global instance
_knowledge_service: Optional[KnowledgeService] = None

def get_knowledge_service() -> KnowledgeService:
    global _knowledge_service
    if _knowledge_service is None:
        _knowledge_service = KnowledgeService()
    return _knowledge_service
