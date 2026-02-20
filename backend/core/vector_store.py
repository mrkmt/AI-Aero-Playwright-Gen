import logging
import os
import uuid
import chromadb
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persistence_path: str = "storage/vector_db"):
        # Make path relative to backend directory
        if not os.path.isabs(persistence_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            persistence_path = os.path.join(base_dir, persistence_path)

        os.makedirs(persistence_path, exist_ok=True)

        try:
            self.client = chromadb.PersistentClient(path=persistence_path)
            logger.info(f"VectorStore initialized at {persistence_path}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.client = None

    async def add_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        collection_name: str = "knowledge",
        doc_id: Optional[str] = None
    ) -> str:
        if not self.client:
            return "error_db_not_initialized"
            
        collection = self.client.get_or_create_collection(name=collection_name)

        if not doc_id:
            doc_id = str(uuid.uuid4())

        # ChromaDB expects list for documents, metadatas, and ids
        collection.upsert(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        return doc_id

    async def search_similar(
        self,
        query: str,
        collection_name: str = "knowledge",
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if not self.client:
            return []
            
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            return []  # Collection doesn't exist

        results = collection.query(
            query_texts=[query],
            n_results=limit,
            where=filter_metadata
        )

        # Format results
        formatted_results = []
        if results and results['ids']:
            ids = results['ids'][0]
            docs = results['documents'][0] if results['documents'] else []
            metas = results['metadatas'][0] if results['metadatas'] else []
            dists = results['distances'][0] if results['distances'] else []

            for i in range(len(ids)):
                # Score is 1.0 - distance (Chroma defaults to L2 distance)
                dist_val = dists[i] if i < len(dists) else 1.0
                score = max(0, 1.0 - dist_val) 
                
                formatted_results.append({
                    "id": ids[i],
                    "content": docs[i] if i < len(docs) else "",
                    "metadata": metas[i] if i < len(metas) else {},
                    "score": score
                })

        return formatted_results

    async def delete_document(self, doc_id: str, collection_name: str = "knowledge") -> bool:
        if not self.client:
            return False
            
        try:
            collection = self.client.get_collection(name=collection_name)
            collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False

    async def get_document(self, doc_id: str, collection_name: str = "knowledge") -> Optional[Dict[str, Any]]:
        if not self.client:
            return None
            
        try:
            collection = self.client.get_collection(name=collection_name)
            result = collection.get(ids=[doc_id])
            if result and result['ids'] and len(result['ids']) > 0:
                return {
                    "id": result['ids'][0],
                    "content": result['documents'][0] if result['documents'] else "",
                    "metadata": result['metadatas'][0] if result['metadatas'] else {}
                }
            return None
        except Exception:
            return None

    async def update_document(
        self, 
        doc_id: str, 
        content: Optional[str] = None, 
        metadata: Optional[Dict[str, Any]] = None,
        collection_name: str = "knowledge"
    ) -> bool:
         if not self.client:
             return False
             
         current = await self.get_document(doc_id, collection_name)
         if not current:
             return False
             
         new_content = content if content is not None else current["content"]
         new_metadata = current["metadata"]
         if metadata:
             new_metadata.update(metadata)
             
         collection = self.client.get_or_create_collection(name=collection_name)
         collection.upsert(
             ids=[doc_id],
             documents=[new_content],
             metadatas=[new_metadata]
         )
         return True
         
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        if not self.client:
            return {"document_count": 0}
            
        try:
             collection = self.client.get_collection(name=collection_name)
             count = collection.count()
             return {"document_count": count}
        except Exception:
             return {"document_count": 0}

_store = None

def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
