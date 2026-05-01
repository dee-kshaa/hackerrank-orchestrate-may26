
# Support Triage RAG Agent

A **terminal-based multi-domain support ticket triage agent** using semantic search and grounded response generation. Process support tickets from HackerRank, Claude, and Visa with zero hallucinations—all responses are grounded in provided documentation.

## Features

✅ **Grounded Responses Only** - Never invents policies; always cites sources
✅ **Smart Escalation** - Auto-escalates fraud, security, and low-confidence cases
✅ **Multi-Domain Support** - HackerRank, Claude, and Visa with product-specific routing
✅ **Semantic Search** - FAISS vector search with all-MiniLM-L6-v2 embeddings
✅ **Safety First** - Detects fraud, unauthorized charges, and security issues
✅ **Comprehensive Logging** - Full audit trail of all decisions
✅ **CSV Export** - Structured data for analysis
✅ **No External Knowledge** - Corpus-only responses, no internet access
✅ **Terminal Only** - No web UI, pure Python CLI

## Architecture

```
Ticket Input
    ↓
[1] CLASSIFY (request_type + product_area)
    ↓
[2] SAFETY CHECK (fraud/unauthorized detection)
    ↓ (High-risk? → ESCALATE)
    ↓
[3] RETRIEVE (FAISS semantic search, top_k=3)
    ↓ (No docs? → ESCALATE)
    ↓
[4] RESPOND (Grounded response generation)
    ↓ (Confidence < 0.3? → ESCALATE)
    ↓
[5] DETERMINE ACTION (REPLY or ESCALATE)
    ↓
[6] EXPORT (CSV + logging)
```

## Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Ingest Corpus

Build FAISS index from support documentation:

```bash
python main.py ingest data/corpus.json
```

This creates:
- `data/faiss_index.bin` - FAISS vector index
- `data/metadata.json` - Document metadata

### 2. Process Tickets

#### Interactive Mode
Process tickets one-by-one with live responses:

```bash
python main.py
```

Then:
1. Enter ticket ID (or press Enter for auto-generated)
2. Enter ticket content (type `END` on a new line to finish)
3. View the response with classification, action, and confidence

Commands:
- `exit` - Quit
- `export` - Save results to CSV
- `clear` - Reset results

#### Batch Mode
Process multiple tickets from JSON file:

```bash
python main.py process data/sample_tickets.json
```

Outputs:
- `output.csv` - Results table
- `log.txt` - Full audit trail

## Configuration

Edit `config.json` to customize:

```json
{
  "embedding_model": "all-MiniLM-L6-v2",
  "retrieval_top_k": 3,
  "min_confidence_threshold": 0.3,
  "chunk_size": 700,
  "chunk_overlap": 80
}
```

## Modules

| Module | Purpose |
|--------|---------|
| `main.py` | Orchestrator, CLI, pipeline management |
| `classify.py` | Request classification (10 types, 3 products) |
| `safety.py` | High-risk detection and escalation logic |
| `retrieve.py` | FAISS semantic search and document retrieval |
| `respond.py` | Grounded response generation from docs |
| `ingest.py` | Corpus ingestion, chunking, embedding |
| `utils.py` | Configuration, logging, utilities |

## Response Pipeline

### Classification Labels

**Request Types (10):**
- `account_access` - Login, password, account access
- `billing` - Charges, invoices, pricing
- `fraud` - Fraud reports, unauthorized charges
- `technical_issue` - Bugs, errors, crashes
- `subscription` - Plan changes, cancellations
- `permissions` - Access control, team management
- `assessment_issue` - Grading, scoring, evaluation
- `refund` - Refund requests
- `security` - 2FA, API keys, breaches
- `general_support` - General inquiries

**Product Areas (3):**
- `Claude` - Claude API, authentication
- `HackerRank` - Assessments, coding challenges
- `Visa` - Payment processing, transactions

**Actions (2):**
- `REPLY` - Confident, safe, grounded response
- `ESCALATE` - High-risk, low-confidence, requires human review

### Escalation Rules

**Always ESCALATE:**
- ❌ Fraud/fraudulent activity
- ❌ Unauthorized charges
- ❌ Hacked/compromised accounts
- ❌ Legal/privacy/security issues
- ❌ Payment disputes, chargebacks
- ❌ Refund requests (require human review)
- ❌ Confidence score < 0.3
- ❌ Insufficient documentation

### Safety Keywords

High-risk keywords that trigger automatic escalation:

```
fraud, unauthorized, stolen, hack, hacked, chargeback,
lawsuit, legal, privacy breach, compromised, identity theft
```

## Output Format

### Console (Interactive)

```
============================================================
Processing ticket: TICKET-00001
============================================================
Step 1: Classification
  Result: type=account_access, product=Claude, confidence=0.950
Step 2: Safety Check
  Result: action=REPLY, risk_level=none
Step 3: Semantic Retrieval
  Result: retrieved 3 documents, confidence=0.852
Step 4: Escalation Check
  Result: action=REPLY, reason=Safe to reply with high confidence
Step 5: Response Generation
  Response length: 387 chars
============================================================

TICKET ID: TICKET-00001
REQUEST TYPE: account_access
PRODUCT AREA: Claude
ACTION: REPLY
CONFIDENCE: 0.852
------------------------------------------------------------
RESPONSE:
To help you regain account access:

Based on our documentation:
- Go to the login page and click 'Forgot password?'
- Enter your email address
- Check for reset email (check spam folder too!)
- Click the reset link and create a new password
- Links expire after 1 hour

---
*Response based on Claude Help Center - Account Access*
------------------------------------------------------------
```

### CSV Export (output.csv)

```csv
ticket_id,request_type,product_area,action,response,confidence,timestamp
TICKET-00001,account_access,Claude,REPLY,"To help you regain account access...",0.852,2026-05-01T12:30:45.123456
TICKET-00002,fraud,Visa,ESCALATE,"This request requires immediate attention...",0.0,2026-05-01T12:31:12.456789
```

### Log File (log.txt)

Complete audit trail with timestamps, classification decisions, safety checks, retrieval details, and response generation logic.

## Sample Usage

### Process Sample Tickets

```bash
python main.py process data/sample_tickets.json
```

Processes 10 test tickets covering all scenarios and exports results.

### Ingest Custom Corpus

Create `custom_corpus.json`:

```json
[
  {
    "product_area": "Claude",
    "category": "billing",
    "source": "My Documentation",
    "content": "Billing information here..."
  }
]
```

Then:

```bash
python main.py ingest custom_corpus.json
```

## Example Scenarios

### 1. Password Reset (REPLY)

**Input:**
```
I forgot my Claude password and can't log in. 
I've tried the password reset but haven't received the email yet. 
What should I do?
```

**Output:**
```
Action: REPLY
Confidence: 0.85
Response: To help you regain account access...
(detailed steps from Claude documentation)
```

### 2. Fraud Report (ESCALATE)

**Input:**
```
Someone made an unauthorized charge of $500 to my Claude account. 
I don't recognize this transaction and want a refund immediately. 
This might be fraud.
```

**Output:**
```
Action: ESCALATE
Confidence: 0.0
Reason: High-risk keyword detected: fraud, unauthorized
Response: This request requires immediate attention from our specialized fraud investigation team...
```

### 3. Account Hacked (ESCALATE)

**Input:**
```
My account appears to be hacked! 
I see login attempts from countries I've never been to, 
and my API key might be compromised. 
Please help immediately!
```

**Output:**
```
Action: ESCALATE
Confidence: 0.0
Reason: High-risk keyword detected: hacked, compromised
Response: This is a security concern and requires immediate investigation...
```

## Performance Considerations

- **Embedding Generation:** ~50ms per 1000 tokens (GPU accelerated)
- **FAISS Search:** <5ms for similarity search
- **Response Generation:** ~100ms per ticket
- **Total Processing Time:** ~200-300ms per ticket

## Limitations & Constraints

- ✅ Responses ONLY from corpus (no external knowledge)
- ✅ No policy inventions or unsupported promises
- ✅ No refund authorization (escalate to humans)
- ✅ Terminal-only (no web UI)
- ✅ No API integrations (pure Python)

## Troubleshooting

### FAISS Index Not Found
```
Run: python main.py ingest data/corpus.json
```

### Low Confidence Scores
- Corpus may not have relevant information
- Try rephrasing the ticket
- Add more documents to corpus

### Tickets Always Escalated
- Check `min_confidence_threshold` in config.json
- Verify corpus relevance
- Review log.txt for escalation reasons

## Dependencies

- `sentence-transformers==2.2.2` - Embedding model
- `faiss-cpu==1.7.4` - Vector search
- `pandas==2.0.3` - CSV export
- `numpy==1.24.3` - Numerical computing
- `python-dotenv==1.0.0` - Configuration
- `requests==2.31.0` - HTTP requests

## License

Proprietary - Support Triage Agent

## Support

For issues or questions, contact the development team.
