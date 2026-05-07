# SentinelIQ AI Service

Flask microservice providing AI-powered text analysis using Groq API (Llama 3.3 70B).

---

## Setup

### Prerequisites
- Python 3.11+
- Redis 7 (for caching)
- Groq API key

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

- **Redis Caching**: SHA256 keys, 15min TTL
- **Security Headers**: X-Content-Type-Options, CSP, HSTS, etc.
- **Fallback Responses**: Graceful degradation on Groq errors
- **Response Time Target**: <2s average per endpoint
- **Input Validation**: Max 1000 chars (2000 for generate-report)

---

## Architecture

```
ai-service/
├── app.py              # Flask app, blueprints, security headers
├── routes/
│   ├── describe.py     # POST /describe endpoint
│   ├── recommend.py    # POST /recommend endpoint
│   └── generate_report.py  # POST /generate-report endpoint
├── services/
│   ├── groq_client.py  # Groq API client with fallback
│   └── cache_service.py    # Redis caching layer
└── prompts/
    ├── describe.txt    # /describe prompt template
    ├── recommend.txt   # /recommend prompt template
    └── generate_report.txt   # /generate-report prompt template
```

---

## Author

AI Developer 1 - SentinelIQ Capstone Project
