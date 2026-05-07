import os
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance
    
    def load_model(self):
        """Pre-load sentence-transformers model at startup"""
        if self._model is None:
            model_name = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
            print(f"Loading sentence-transformers model: {model_name}")
            try:
                self._model = SentenceTransformer(model_name)
                print(f"Model loaded successfully. Embedding dimension: {self._model.get_sentence_embedding_dimension()}")
            except Exception as e:
                print(f"Failed to load embedding model: {e}")
                self._model = None
        return self._model
    
    def encode(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if self._model is None:
            self.load_model()
        
        if self._model is None:
            return None
        
        try:
            embedding = self._model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            print(f"Embedding generation failed: {e}")
            return None
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        emb1 = self.encode(text1)
        emb2 = self.encode(text2)
        
        if emb1 is None or emb2 is None:
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._model is not None
