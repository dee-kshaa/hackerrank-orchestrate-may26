"""Retrieval module for finding relevant documents."""
import json
import os
from typing import Dict, Any, List, Tuple

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    faiss = None
    SentenceTransformer = None


def retrieve_documents(query: str, config: Dict[str, Any], output_dir: str = '.', k: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieve top-k most similar documents for a query.
    
    Args:
        query: Query text
        config: Configuration dict
        output_dir: Directory containing FAISS index
        k: Number of documents to retrieve
        
    Returns:
        List of retrieved documents
    """
    index_path = os.path.join(output_dir, 'faiss_index.bin')
    metadata_path = os.path.join(output_dir, 'index_metadata.json')
    
    if not os.path.exists(metadata_path):
        print("Index metadata not found. Run ingest first.")
        return []
    
    if SentenceTransformer is None:
        print("sentence-transformers not installed - returning empty results")
        return []
    
    # Load metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    documents = metadata.get('documents', [])
    model_name = metadata.get('model', 'all-MiniLM-L6-v2')
    
    if not os.path.exists(index_path):
        print("FAISS index not found.")
        return []
    
    # Load model and index
    model = SentenceTransformer(model_name)
    index = faiss.read_index(index_path)
    
    # Encode query
    query_embedding = model.encode([query], show_progress_bar=False).astype('float32')
    
    # Search
    distances, indices = index.search(query_embedding, k)
    
    # Retrieve documents
    results = []
    for idx in indices[0]:
        if 0 <= idx < len(documents):
            results.append(documents[int(idx)])
    
    return results
