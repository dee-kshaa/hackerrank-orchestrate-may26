"""Ingestion module for building vector index from corpus."""
import json
import os
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Warning: faiss and/or sentence-transformers not installed")
    faiss = None
    SentenceTransformer = None


def load_corpus_from_file(corpus_path: str) -> List[Dict[str, Any]]:
    """
    Load corpus from either JSON or CSV file.
    
    Args:
        corpus_path: Path to corpus file (JSON or CSV)
        
    Returns:
        List of document dictionaries
    """
    if corpus_path.endswith('.csv'):
        # Load CSV
        df = pd.read_csv(corpus_path)
        documents = []
        
        for idx, row in df.iterrows():
            # Create document from CSV row
            doc = {
                'id': str(idx),
                'title': str(row.get('Subject', row.get('Issue', f'Document {idx}'))),
                'content': ' '.join([f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])]),
                'company': row.get('Company', 'Unknown'),
                'issue': row.get('Issue', row.get('issue', '')),
                'subject': row.get('Subject', row.get('subject', '')),
                'product_area': row.get('Product Area', row.get('product_area', '')),
                'request_type': row.get('Request Type', row.get('request_type', '')),
            }
            documents.append(doc)
        
        return documents
    
    elif corpus_path.endswith('.json'):
        # Load JSON
        with open(corpus_path, 'r') as f:
            data = json.load(f)
        
        # Handle both list and dict with 'documents' key
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get('documents', [])
        else:
            return []
    
    else:
        raise ValueError(f"Unsupported file format: {corpus_path}. Use .csv or .json")


def ingest_corpus(corpus_path: str, config: Dict[str, Any] = None, output_dir: str = '.') -> None:
    """
    Load corpus and build FAISS vector index.
    
    Supports both JSON and CSV formats.
    
    Args:
        corpus_path: Path to corpus file (JSON or CSV)
        config: Configuration dict with model settings
        output_dir: Directory to save index and metadata
    """
    if config is None:
        config = {
            'embedding_model': 'all-MiniLM-L6-v2'
        }
    
    if not os.path.exists(corpus_path):
        print(f"Corpus file not found: {corpus_path}")
        return
    
    # Load corpus from file
    print(f"Loading corpus from {corpus_path}...")
    documents = load_corpus_from_file(corpus_path)
    
    if not documents:
        print("No documents in corpus")
        return
    
    print(f"Loaded {len(documents)} documents")
    
    if SentenceTransformer is None:
        print("Skipping vectorization - sentence-transformers not installed")
        # Save corpus as JSON
        metadata = {
            'documents': documents,
            'model': None,
            'dimension': None,
            'count': len(documents)
        }
        with open(os.path.join(output_dir, 'index_metadata.json'), 'w') as f:
            json.dump(metadata, f)
        return
    
    # Initialize model
    model_name = config.get('embedding_model', 'all-MiniLM-L6-v2')
    print(f"Using model: {model_name}")
    model = SentenceTransformer(model_name)
    
    # Extract texts - prefer 'content' field, fallback to 'title'
    texts = []
    for doc in documents:
        text = doc.get('content', doc.get('title', doc.get('text', '')))
        texts.append(str(text))
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = embeddings.astype('float32')
    
    # Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Save index and metadata
    faiss.write_index(index, os.path.join(output_dir, 'faiss_index.bin'))
    
    metadata = {
        'documents': documents,
        'model': model_name,
        'dimension': dimension,
        'count': len(documents)
    }
    with open(os.path.join(output_dir, 'index_metadata.json'), 'w') as f:
        json.dump(metadata, f)
    
    print(f"Index built with {len(documents)} documents")
    print(f"Saved to {output_dir}/")


def ingest(corpus_path: str, config: Dict[str, Any] = None, output_dir: str = '.') -> Tuple[bool, str]:
    """
    Wrapper function for ingestion that returns success/error tuple.
    
    Args:
        corpus_path: Path to corpus file
        config: Configuration dict
        output_dir: Output directory
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        ingest_corpus(corpus_path, config, output_dir)
        return True, f"Successfully ingested corpus from {corpus_path}"
    except Exception as e:
        return False, f"Error ingesting corpus: {str(e)}"
