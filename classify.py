"""Ticket classification module."""
import json
from typing import Dict, Any


def classify_request(content: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Classify a support request into request type and product area.
    
    Args:
        content: Request text to classify
        config: Optional configuration dict with classifier settings
        
    Returns:
        Dictionary with request_type, product_area, and confidence scores
    """
    if config is None:
        config = {
            'request_types': ['bug', 'feature_request', 'account_issue', 'billing', 'general'],
            'product_areas': ['Claude', 'HackerRank', 'Visa', 'unknown'],
            'keywords': {
                'bug': ['error', 'not working', 'broken', 'issue', 'fail', 'crash', 'blocker'],
                'feature_request': ['add', 'implement', 'new', 'feature', 'please add', 'can you add'],
                'account_issue': ['access', 'login', 'password', 'account', 'removed', 'seat'],
                'billing': ['payment', 'charge', 'refund', 'money', 'subscription', 'invoice'],
                'Claude': ['claude', 'ai assistant'],
                'HackerRank': ['hackerrank', 'assessment', 'test'],
                'Visa': ['visa', 'card', 'payment'],
            }
        }
    
    text = content.lower()
    
    # Classify request type
    request_type = 'general'
    request_confidence = 0.3
    
    for req_type, keywords in config.get('keywords', {}).items():
        if req_type in config.get('request_types', []):
            for keyword in keywords:
                if keyword in text:
                    request_type = req_type
                    request_confidence = 0.7
                    break
    
    # Classify product area
    product_area = 'unknown'
    product_confidence = 0.3
    
    if 'claude' in text:
        product_area = 'Claude'
        product_confidence = 0.8
    elif 'hackerrank' in text or 'assessment' in text or 'test' in text:
        product_area = 'HackerRank'
        product_confidence = 0.8
    elif 'visa' in text or 'card' in text or 'payment' in text:
        product_area = 'Visa'
        product_confidence = 0.8
    
    return {
        'request_type': request_type,
        'product_area': product_area,
        'confidence': min(request_confidence, product_confidence),
        'request_confidence': request_confidence,
        'product_confidence': product_confidence
    }
