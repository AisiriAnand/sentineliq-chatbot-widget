# SentinelIQ AI Service

Flask microservice providing AI-powered text analysis using Groq API (Llama 3.3 70B).

---

## Setup

### Prerequisites
- Python 3.11+
- Redis 7 (for caching)
- Groq API key
- 500MB disk space (for sentence-transformers model)
- 100MB disk space (for ChromaDB)

### Manual Setup Steps (REQUIRED)

After installation, you **MUST** run these manually:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed ChromaDB with domain knowledge (10 documents)
python scripts/seed_chroma.py

# 3. Start the AI service
python app.py

# 4. In another terminal, run demo tests (30 records)
python scripts/run_demo.py
```

**Step 2** creates the vector database with 10 FAQ documents.
**Step 4** generates `demo_outputs.json` with results for all 30 test records.

### Installation

```bash
cd ai-service
pip install -r requirements.txt
```

### Environment Variables

Create `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
AI_PORT=5000
FLASK_DEBUG=false
REDIS_URL=redis://localhost:6379/0
```

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key | Yes |
| `AI_PORT` | Service port (default: 5000) | No |
| `FLASK_DEBUG` | Debug mode (default: false) | No |
| `REDIS_URL` | Redis connection URL | No |
| `EMBEDDING_MODEL` | Sentence-transformers model (default: all-MiniLM-L6-v2) | No |
| `ALLOWED_ORIGIN` | CORS allowed origin (default: *) | No |

---

## Run Instructions

### Local Development

```bash
python app.py
```

Service runs on `http://localhost:5000`

### Docker

```bash
docker build -t sentineliq-ai .
docker run -p 5000:5000 --env-file .env sentineliq-ai
```

### Health Check

```bash
curl http://localhost:5000/health
```

---

## API Reference

### POST /describe

Analyze user query and return structured description with intent, sentiment, priority.

**Request:**
```bash
curl -X POST http://localhost:5000/describe \
  -H "Content-Type: application/json" \
  -d '{"user_input": "My internet is not working since morning"}'
```

**Response:**
```json
{
  "description": "User reports internet connectivity issue persisting since morning",
  "intent": "technical_support",
  "sentiment": "negative",
  "priority": "high",
  "suggested_action": "Escalate to network support team for immediate resolution",
  "generated_at": "2026-05-07T08:30:00"
}
```

**Error (Fallback):**
```json
{
  "description": "Unable to process request - AI service temporarily unavailable",
  "intent": "other",
  "sentiment": "neutral",
  "priority": "low",
  "suggested_action": "Retry request or contact support",
  "is_fallback": true,
  "generated_at": "2026-05-07T08:30:00"
}
```

---

### POST /recommend

Generate 3 actionable recommendations for user query.

**Request:**
```bash
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_input": "System keeps crashing after update"}'
```

**Response:**
```json
{
  "recommendations": [
    {
      "action_type": "troubleshoot",
      "description": "Check system logs for error details and rollback recent update",
      "priority": "high"
    },
    {
      "action_type": "document",
      "description": "Log crash details with timestamps for engineering team",
      "priority": "medium"
    },
    {
      "action_type": "follow_up",
      "description": "Schedule follow-up to verify resolution within 24 hours",
      "priority": "medium"
    }
  ],
  "generated_at": "2026-05-07T08:30:00"
}
```

---

### POST /generate-report

Generate comprehensive report with title, summary, overview, key items, recommendations.

**Request:**
```bash
curl -X POST http://localhost:5000/generate-report \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Customer reported billing discrepancy of $500, account shows double charge"}'
```

**Response:**
```json
{
  "title": "Billing Discrepancy Report",
  "summary": "Customer identified $500 double charge on account requiring immediate billing team review",
  "overview": "Customer report indicates significant billing error with duplicate charge. Account review needed to verify transaction history and process refund if confirmed.",
  "key_items": [
    "$500 billing discrepancy reported",
    "Double charge suspected on account",
    "Customer requires resolution and potential refund"
  ],
  "recommendations": [
    "Verify transaction history for duplicate charge",
    "Process refund if double charge confirmed",
    "Update customer on resolution status within 24 hours"
  ],
  "generated_at": "2026-05-07T08:30:00"
}
```

---

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (missing/invalid user_input) |
| 500 | Internal Server Error |

---

## Features

- **Sentence-Transformers**: Pre-loaded at startup for semantic similarity
- **Redis Caching**: SHA256 keys, 15min TTL
- **Rate Limiting**: 100 req/min, 1000 req/hour per IP
- **Security Headers**: X-Content-Type-Options, CSP, HSTS, CORS, etc.
- **Content-Type Validation**: Enforces application/json for POST
- **Fallback Responses**: Graceful degradation on Groq errors
- **Response Time Target**: <2s average per endpoint
- **Input Validation**: Max 1000 chars (2000 for generate-report)

---

## Architecture

```
ai-service/
├── app.py                  # Flask app, rate limiting, security headers
├── routes/
│   ├── describe.py         # POST /describe endpoint
│   ├── recommend.py        # POST /recommend endpoint
│   └── generate_report.py  # POST /generate-report endpoint
├── services/
│   ├── groq_client.py      # Groq API client with fallback
│   ├── cache_service.py    # Redis caching layer
│   └── embedding_service.py    # Sentence-transformers pre-loaded
└── prompts/
    ├── describe.txt        # /describe prompt template
    ├── recommend.txt       # /recommend prompt template
    └── generate_report.txt # /generate-report prompt template
```

---

## Author

AI Developer 1 - SentinelIQ Capstone Project
