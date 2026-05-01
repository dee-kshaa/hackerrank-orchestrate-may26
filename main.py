"""
Main orchestrator for Support Triage RAG Agent
Coordinates classification, safety, retrieval, and response generation
"""

import sys
import json
import csv
from datetime import datetime
from utils import (
    load_config, setup_logging, validate_ticket, format_response, 
    get_timestamp, ensure_data_dir, config, logger
)
from classify import classify_request
from safety import check_safety, should_escalate
from respond import generate_response, should_escalate_on_confidence
from ingest import ingest

def process_ticket(ticket: dict) -> dict:
    """
    Process a single support ticket through the entire pipeline.
    
    Returns result dict with full ticket processing details.
    """
    
    ticket_id = ticket.get('ticket_id', f"AUTO-{int(datetime.now().timestamp())}")
    content = ticket.get('content', '').strip()
    
    # Validate
    valid, msg = validate_ticket(ticket)
    if not valid:
        logger.error(f"Invalid ticket: {msg}")
        return {
            "ticket_id": ticket_id,
            "request_type": "unknown",
            "product_area": "unknown",
            "action": "ESCALATE",
            "response": f"Invalid ticket: {msg}",
            "confidence": 0.0,
            "timestamp": get_timestamp()
        }
    
    logger.info(f"\n{'='*70}")
    logger.info(f"Processing ticket: {ticket_id}")
    logger.info(f"{'='*70}")
    
    # Step 1: Classify
    logger.info("[STEP 1] Classification")
    classification = classify_request(content)
    request_type = classification['request_type']
    product_area = classification['product_area']
    class_confidence = classification['confidence']
    
    logger.info(f"  Request Type: {request_type} (confidence: {classification['request_confidence']:.3f})")
    logger.info(f"  Product Area: {product_area} (confidence: {classification['product_confidence']:.3f})")
    
    # Step 2: Safety Check
    logger.info("[STEP 2] Safety Check")
    safety_check = check_safety(content, request_type)
    risk_level = safety_check['risk_level']
    
    logger.info(f"  Risk Level: {risk_level}")
    
    if should_escalate(safety_check):
        logger.info(f"[STEP 5] Escalation Check")
        logger.info(f"  Action: ESCALATE (high-risk content)")
        
        logger.info(f"\n{'-'*70}")
        logger.info("RESULT:")
        logger.info(f"  Ticket ID: {ticket_id}")
        logger.info(f"  Request Type: {request_type}")
        logger.info(f"  Product Area: {product_area}")
        logger.info(f"  Action: ESCALATE")
        logger.info(f"  Confidence: 0.0%")
        logger.info(f"  Response: {safety_check['reason']}")
        logger.info(f"{'-'*70}\n")
        
        return {
            "ticket_id": ticket_id,
            "request_type": request_type,
            "product_area": product_area,
            "action": "ESCALATE",
            "response": safety_check['reason'],
            "confidence": 0.0,
            "timestamp": get_timestamp()
        }
    
    # Step 3: Retrieval
    logger.info("[STEP 3] Semantic Retrieval")
    
    # Step 4: Response Generation
    logger.info("[STEP 4] Response Generation")
    response_result = generate_response(
        content,
        request_type,
        product_area,
        class_confidence
    )
    
    response_text = response_result['response']
    retrieval_confidence = response_result['confidence']
    
    logger.info(f"  Confidence: {retrieval_confidence:.3f}")
    logger.info(f"  Retrieved docs: {len(response_result['retrieved_documents'])}")
    
    # Step 5: Escalation Decision
    logger.info("[STEP 5] Escalation Check")
    
    should_esc, reason = should_escalate_on_confidence(retrieval_confidence)
    
    if should_esc:
        action = "ESCALATE"
        logger.info(f"  Action: ESCALATE (low confidence: {reason})")
    else:
        action = "REPLY"
        logger.info(f"  Action: REPLY (high confidence)")
    
    # Final confidence
    final_confidence = retrieval_confidence if action == "REPLY" else 0.0
    
    # Log result
    logger.info(f"\n{'-'*70}")
    logger.info("RESULT:")
    logger.info(f"  Ticket ID: {ticket_id}")
    logger.info(f"  Request Type: {request_type}")
    logger.info(f"  Product Area: {product_area}")
    logger.info(f"  Action: {action}")
    logger.info(f"  Confidence: {final_confidence:.1%}")
    logger.info(f"  Response: {response_text[:100]}...")
    logger.info(f"{'-'*70}\n")
    
    return {
        "ticket_id": ticket_id,
        "request_type": request_type,
        "product_area": product_area,
        "action": action,
        "response": response_text,
        "confidence": final_confidence,
        "timestamp": get_timestamp()
    }

def process_batch(batch_file: str) -> list:
    """Process batch of tickets from JSON file."""
    
    logger.info(f"Starting batch processing from {batch_file}")
    
    try:
        with open(batch_file, 'r') as f:
            tickets = json.load(f)
        
        if not isinstance(tickets, list):
            logger.error("Batch file must contain a JSON array")
            return []
        
        logger.info(f"Loaded {len(tickets)} tickets from batch file")
        
        results = []
        for idx, ticket in enumerate(tickets, 1):
            logger.info(f"\n[{idx}/{len(tickets)}] Processing batch ticket...")
            result = process_ticket(ticket)
            results.append(result)
        
        # Export to CSV
        export_results(results)
        
        logger.info(f"\n✓ Batch processing completed! Processed {len(results)} tickets")
        logger.info(f"Results exported to output.csv")
        
        return results
    
    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        return []

def export_results(results: list, output_file: str = "output.csv"):
    """Export results to CSV."""
    
    if not results:
        logger.warning("No results to export")
        return
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['ticket_id', 'request_type', 'product_area', 'action', 'confidence', 'response', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        logger.info(f"Results exported to {output_file}")
    
    except Exception as e:
        logger.error(f"Error exporting results: {e}")

def interactive_mode():
    """Interactive mode for processing tickets one by one."""
    
    logger.info("\n" + "="*70)
    logger.info("Support Triage RAG Agent - Interactive Mode")
    logger.info("="*70 + "\n")
    
    results = []
    ticket_counter = 1
    
    print("\nCommands: 'exit', 'export', 'clear', or enter ticket details")
    print("-" * 70)
    
    while True:
        try:
            # Get ticket ID
            ticket_id = input("\nTicket ID (auto-generate: press Enter): ").strip()
            if ticket_id.lower() == 'exit':
                break
            elif ticket_id.lower() == 'export':
                export_results(results)
                continue
            elif ticket_id.lower() == 'clear':
                results = []
                ticket_counter = 1
                logger.info("Results cleared")
                continue
            
            if not ticket_id:
                ticket_id = f"TICKET-{ticket_counter:05d}"
                ticket_counter += 1
            
            # Get ticket content
            print("Enter ticket content (type 'END' on a new line to finish):")
            lines = []
            while True:
                line = input()
                if line.upper() == 'END':
                    break
                lines.append(line)
            
            content = "\n".join(lines).strip()
            
            if not content:
                logger.warning("Empty ticket content")
                continue
            
            # Process ticket
            ticket = {
                "ticket_id": ticket_id,
                "content": content
            }
            
            result = process_ticket(ticket)
            results.append(result)
            
            # Display result
            print(format_response(result))
        
        except KeyboardInterrupt:
            logger.info("\n\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            continue

def main():
    """Main entry point."""
    
    # Setup
    load_config()
    setup_logging()
    ensure_data_dir()
    
    logger.info("Support Triage RAG Agent Started")
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "ingest":
            # Ingest corpus
            corpus_path = sys.argv[2] if len(sys.argv) > 2 else "data/corpus.json"
            logger.info(f"Ingesting corpus from {corpus_path}")
            success, message = ingest(corpus_path)
            print(message)
            if success:
                print(f"✓ Corpus ingestion completed successfully!")
            else:
                print(f"✗ Ingestion failed")
                sys.exit(1)
        
        elif command == "process":
            # Process batch
            batch_file = sys.argv[2] if len(sys.argv) > 2 else "data/sample_tickets.json"
            results = process_batch(batch_file)
            
            # Summary
            if results:
                reply_count = sum(1 for r in results if r['action'] == 'REPLY')
                escalate_count = sum(1 for r in results if r['action'] == 'ESCALATE')
                avg_confidence = sum(r['confidence'] for r in results) / len(results)
                
                print(f"\n{'='*70}")
                print("BATCH PROCESSING SUMMARY")
                print(f"{'='*70}")
                print(f"Total Tickets: {len(results)}")
                print(f"Replies: {reply_count}")
                print(f"Escalations: {escalate_count}")
                print(f"Avg Confidence: {avg_confidence:.1%}")
                print(f"{'='*70}\n")
        
        else:
            print(f"Unknown command: {command}")
            print("Usage:")
            print("  python main.py ingest [corpus_path]")
            print("  python main.py process [batch_file]")
            print("  python main.py (interactive mode)")
    
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
