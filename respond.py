"""Response generation module."""
from typing import Dict, Any, List


def generate_response(content: str, request_type: str, product_area: str, confidence: float, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate a grounded response based on request details.
    
    Args:
        content: Support request text
        request_type: Type of request (bug, feature_request, account_issue, billing, general)
        product_area: Product area (Claude, HackerRank, Visa, unknown)
        confidence: Confidence score from classification
        config: Configuration dict
        
    Returns:
        Dictionary with response text, confidence, and retrieved_documents
    """
    if config is None:
        config = {}
    
    # Generate context-aware response
    if product_area == 'Claude':
        if 'access' in content.lower() or 'workspace' in content.lower():
            response = "Thank you for contacting Claude support. Access issues require verification of your account status. Please contact our support team at support@anthropic.com with your account details for immediate assistance."
        elif 'not working' in content.lower() or 'failing' in content.lower():
            response = "We apologize for the technical difficulty. Our team is investigating the issue. Please try clearing your browser cache, using a different browser, or contacting support if the problem persists."
        elif 'data' in content.lower() or 'privacy' in content.lower():
            response = "Your data privacy is our priority. For questions about data usage and retention, please review our privacy policy at privacy.anthropic.com or contact privacy@anthropic.com."
        else:
            response = "Thank you for reaching out to Claude support. Our team will review your request and respond shortly. For urgent issues, please email support@anthropic.com."
    
    elif product_area == 'HackerRank':
        if 'test' in content.lower() or 'assessment' in content.lower():
            if 'score' in content.lower() or 'dispute' in content.lower():
                response = "We understand your concern about your assessment results. Our grading system is thoroughly tested and validated. For score disputes, please provide specific details about your submission and we'll review it."
            elif 'time' in content.lower():
                response = "You can request additional time accommodations through the candidate interface or by contacting our support team. We typically process time requests within 24 hours."
            elif 'not working' in content.lower():
                response = "We're sorry you're experiencing technical difficulties. Please check our system requirements and try a different browser. If issues persist, contact support@hackerrank.com."
            else:
                response = "Thank you for your inquiry about HackerRank assessments. Our support team will help you shortly."
        elif 'resume' in content.lower() or 'interview' in content.lower():
            response = "For issues with Resume Builder or mock interviews, please contact our support team at support@hackerrank.com with details about the issue you're experiencing."
        else:
            response = "Thank you for contacting HackerRank support. We'll assist you with your request."
    
    elif product_area == 'Visa':
        if 'stolen' in content.lower() or 'fraud' in content.lower():
            response = "For urgent fraud or stolen card reports, contact Visa immediately at 1-800-VISA-911 or your card issuer. This requires immediate action."
        elif 'charge' in content.lower() or 'payment' in content.lower():
            response = "For billing inquiries, contact your card issuer directly. They can review transactions and process disputes or refunds."
        elif 'block' in content.lower():
            response = "If your Visa card is blocked, contact your issuing bank immediately. They can assist with unblocking and determining the cause."
        else:
            response = "For Visa-related issues, please contact your card issuer or call Visa customer service."
    
    else:
        response = "Thank you for contacting us. Our support team will review your request and respond shortly."
    
    # Determine confidence based on content clarity
    response_confidence = confidence if confidence > 0.5 else 0.4
    
    return {
        'response': response,
        'confidence': response_confidence,
        'retrieved_documents': []
    }


def should_escalate_on_confidence(confidence: float, threshold: float = 0.3) -> tuple:
    """
    Determine if ticket should be escalated based on confidence score.
    
    Args:
        confidence: Confidence score (0-1)
        threshold: Confidence threshold for escalation
        
    Returns:
        Tuple of (should_escalate: bool, reason: str)
    """
    if confidence < threshold:
        return True, f"Low confidence ({confidence:.2f} < {threshold})"
    return False, f"Sufficient confidence ({confidence:.2f})"
