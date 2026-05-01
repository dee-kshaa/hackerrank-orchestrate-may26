"""
Utility functions for Support Triage RAG Agent.
Handles config loading, logging, validation, and formatting.
"""

import json
import logging
import os
from datetime import datetime
from typing import Tuple, Dict, Any

# Global config and logger
config = {}
logger = logging.getLogger(__name__)


def load_config(config_path: str = 'config.json') -> Dict[str, Any]:
    """Load configuration from JSON file."""
    global config
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        # Default config fallback
        config = {
            'embedding_model': 'all-MiniLM-L6-v2',
            'faiss_index_path': 'data/faiss_index.bin',
            'metadata_path': 'data/metadata.json',
            'corpus_path': 'data/corpus.json',
            'output_csv': 'output.csv',
            'log_file': 'log.txt',
            'log_level': 'INFO',
            'chunk_size': 700,
            'chunk_overlap': 80,
            'retrieval_top_k': 3,
            'min_confidence_threshold': 0.3,
            'high_risk_keywords': [
                'fraud', 'unauthorized', 'stolen', 'hack', 'hacked',
                'chargeback', 'lawsuit', 'legal', 'privacy breach',
                'compromised', 'identity theft'
            ]
        }
        return config


def setup_logging() -> logging.Logger:
    """Configure logging to console and file."""
    global logger
    
    log_level = getattr(logging, config.get('log_level', 'INFO').upper(), logging.INFO)
    log_file = config.get('log_file', 'log.txt')
    
    # Clear existing handlers
    logger.handlers.clear()
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_timestamp() -> str:
    """Return current ISO timestamp."""
    return datetime.now().isoformat()


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    os.makedirs('data', exist_ok=True)


def validate_ticket(ticket: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate ticket structure."""
    
    if not isinstance(ticket, dict):
        return False, "Ticket must be a dictionary"
    
    if 'content' not in ticket:
        return False, "Ticket missing 'content' field"
    
    if not ticket.get('content', '').strip():
        return False, "Ticket content cannot be empty"
    
    return True, "Valid ticket"


def format_response(result: Dict[str, Any]) -> str:
    """Format result for terminal output."""
    
    return f"""
{'='*70}
TICKET RESPONSE
{'='*70}
Ticket ID:      {result.get('ticket_id', 'N/A')}
Request Type:   {result.get('request_type', 'N/A')}
Product Area:   {result.get('product_area', 'N/A')}
Action:         {result.get('action', 'N/A')}
Confidence:     {result.get('confidence', 0.0):.1%}
{'='*70}
RESPONSE:
{result.get('response', 'No response generated')}
{'='*70}
"""


def safe_load_json(file_path: str, default=None):
    """Safely load JSON file with fallback."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}
