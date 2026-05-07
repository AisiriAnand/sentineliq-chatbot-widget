# AI Service Demo Script

## 🎯 Problem Statement (1 Sentence)

**"Customer support teams waste hours manually categorizing and routing user queries - our AI service automatically analyzes, describes, recommends actions, and generates reports in under 2 seconds."**

---

## 🏗️ Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   User Query    │────▶│   AI Service     │────▶│  Structured    │
│   (Text Input)  │     │   (Flask/Groq)   │     │  JSON Response │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │  /describe  │     │ /recommend  │     │/gen-report  │
   │  (Intent)   │     │  (Actions)  │     │  (Report)   │
   └─────────────┘     └─────────────┘     └─────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Redis Cache       │
                    │   (15min TTL)       │
                    └─────────────────────┘
```

---

## 🚀 Live Demo Steps

### Step 1: Launch the Tool

```bash
# Terminal 1: Start the AI service
cd ai-service
python app.py
```

**What AI is doing:**
- Loading sentence-transformers model (all-MiniLM-L6-v2) into memory
- Connecting to Redis cache
- Initializing ChromaDB vector database
- Starting Flask server on port 5000

---

### Step 2: Health Check

```bash
curl http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "model": "llama-3.3-70b-versatile",
  "embedding_status": "loaded",
  "redis_status": "connected",
  "avg_response_time_ms": 850.5,
  "uptime_hours": 0.05
}
```

**What AI is doing:**
- Reporting service health
- Showing model status (Llama 3.3 70B via Groq)
- Displaying average response time (target: <2s)
- Confirming embedding service loaded

---

### Step 3: Create Record - /describe

**User Query:** "My internet has been down since this morning and I need it fixed urgently for work"

```bash
curl -X POST http://localhost:5000/describe \
  -H "Content-Type: application/json" \
  -d '{"user_input": "My internet has been down since this morning and I need it fixed urgently for work"}'
```

**What AI is doing:**
1. **Analyzing text** with Llama 3.3 70B
2. **Extracting intent:** "technical_support"
3. **Detecting sentiment:** "negative" (user frustrated)
4. **Setting priority:** "high" (urgent for work)
5. **Generating description:** Brief summary of the issue
6. **Suggesting action:** One-sentence recommendation

**Response Time:** ~800ms (cached: <100ms)

---

### Step 4: Get Recommendations - /recommend

```bash
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_input": "My internet has been down since this morning and I need it fixed urgently for work"}'
```

**What AI is doing:**
1. **Analyzing context** with Llama 3.3 70B
2. **Generating 3 specific actions:**
   - Priority-based ordering
   - Actionable descriptions
   - Type classification (escalate/troubleshoot/follow_up)
3. **Checking Redis cache** first (SHA256 key)
4. **Returning structured JSON** with 3 recommendations

**Response Time:** ~900ms (cached: <100ms)

---

### Step 5: Generate Report - /generate-report

```bash
curl -X POST http://localhost:5000/generate-report \
  -H "Content-Type: application/json" \
  -d '{"user_input": "My internet has been down since this morning and I need it fixed urgently for work"}'
```

**What AI is doing:**
1. **Creating comprehensive analysis** with Llama 3.3 70B
2. **Generating:**
   - **Title:** Concise report name
   - **Summary:** Executive summary
   - **Overview:** Detailed context
   - **Key Items:** 3-5 bullet points
   - **Recommendations:** 3-5 actionable items
3. **Adding timestamp** (generated_at)
4. **Caching result** for 15 minutes

**Response Time:** ~1200ms (cached: <100ms)

---

## 🔄 What Happens Behind the Scenes

### First Request (No Cache):
```
User Input → SHA256 Hash → Miss (not in Redis)
         ↓
   Call Groq API (Llama 3.3 70B)
         ↓
   Response (~800-1200ms)
         ↓
   Store in Redis (15min TTL)
         ↓
   Return JSON
```

### Cached Request:
```
User Input → SHA256 Hash → Hit (in Redis)
         ↓
   Return from Cache (<100ms)
```

### Fallback (Groq Error):
```
User Input → Groq API Error
         ↓
   Return Template with is_fallback: true
         ↓
   Client knows it's degraded response
```

---

## 📊 Performance Targets

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Response Time | <2s | ~0.8-1.2s | ✅ |
| Cache Hit | N/A | <100ms | ✅ |
| Fallback | Graceful | is_fallback flag | ✅ |
| Security | ZAP Zero | Critical/High=0 | ✅ |

---

## 🎤 Demo Script (What to Say)

**Introduction:**
> "This is SentinelIQ AI Service. It automatically analyzes customer support queries using Llama 3.3 70B via Groq API."

**During /describe:**
> "The AI is analyzing the user's intent, sentiment, and priority. It's classifying this as a technical support issue with high priority."

**During /recommend:**
> "Now the AI is generating 3 specific action recommendations, ordered by priority. These are actionable suggestions for support agents."

**During /generate-report:**
> "Finally, the AI creates a comprehensive report with title, summary, key items, and recommendations - all in structured JSON format."

**Conclusion:**
> "With Redis caching, repeated queries return in under 100ms. If Groq fails, we gracefully fall back with is_fallback flag."

---

## ✅ Pre-Demo Checklist

- [ ] `pip install -r requirements.txt` completed
- [ ] `python scripts/seed_chroma.py` run
- [ ] `python app.py` running (check health endpoint)
- [ ] `python scripts/run_demo.py` passed (30 records)
- [ ] `docker build -t sentineliq-ai .` successful
- [ ] All 3 endpoints respond with valid JSON
- [ ] Response times <2s
- [ ] Fallback working (test with invalid API key temporarily)

---

## 📁 Files to Show Mentor

1. **Dockerfile** - Builds cleanly
2. **requirements.txt** - Exact versions pinned
3. **.env.example** - Complete configuration
4. **README.md** - Setup + API reference
5. **SECURITY.md** - ZAP scan results (zero findings)
6. **demo_outputs.json** - 30 test results

---

## 🔗 GitHub Repository

**Your Fork:** `https://github.com/AisiriAnand/sentineliq-chatbot-widget`

**Pull Request:** Against `tecsxpert/sentineliq-chatbot-widget:main`

---

## 🎉 Celebrate the Sprint!

**What You Built:**
- ✅ Flask microservice with 3 AI endpoints
- ✅ Groq API integration (Llama 3.3 70B)
- ✅ Redis caching (SHA256, 15min TTL)
- ✅ Sentence-transformers pre-loaded
- ✅ ChromaDB vector database (10 docs)
- ✅ Rate limiting (100/min, 1000/hour)
- ✅ Security headers (ZAP zero findings)
- ✅ Fallback templates (is_fallback flag)
- ✅ <2s response time target
- ✅ Dockerfile (builds cleanly)
- ✅ Complete documentation

**Well done! 🎊**
