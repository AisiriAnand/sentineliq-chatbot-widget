import os
import chromadb
from chromadb.config import Settings
from services.embedding_service import EmbeddingService

class ChromaService:
    def __init__(self, embedding_service=None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.client = None
        self.collection = None
        self._init_db()
    
    def _init_db(self):
        """Initialize ChromaDB with persistent storage"""
        try:
            db_path = os.getenv('CHROMA_DB_PATH', './chroma_db')
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=db_path
            ))
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="domain_knowledge",
                metadata={"description": "Chatbot domain knowledge documents"}
            )
            print(f"ChromaDB initialized at: {db_path}")
        except Exception as e:
            print(f"ChromaDB initialization failed: {e}")
            self.client = None
            self.collection = None
    
    def add_document(self, doc_id: str, text: str, metadata: dict = None):
        """Add a document to ChromaDB"""
        if self.collection is None:
            print("ChromaDB not available")
            return False
        
        try:
            # Generate embedding
            embedding = self.embedding_service.encode(text)
            if embedding is None:
                print(f"Failed to generate embedding for: {doc_id}")
                return False
            
            # Add to collection
            self.collection.add(
                ids=[doc_id],
                documents=[text],
                embeddings=[embedding.tolist()],
                metadatas=[metadata or {}]
            )
            return True
        except Exception as e:
            print(f"Failed to add document {doc_id}: {e}")
            return False
    
    def search(self, query: str, n_results: int = 3):
        """Search for similar documents"""
        if self.collection is None:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.encode(query)
            if query_embedding is None:
                return []
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results
            )
            
            # Format results
            documents = []
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'id': results['ids'][0][i],
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                })
            return documents
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    def get_collection_count(self):
        """Get number of documents in collection"""
        if self.collection is None:
            return 0
        try:
            return self.collection.count()
        except:
            return 0
    
    def persist(self):
        """Persist database to disk"""
        if self.client:
            try:
                self.client.persist()
                print("ChromaDB persisted to disk")
            except Exception as e:
                print(f"Failed to persist: {e}")
