# Describe Prompt - Test Inputs & Refinement

## Test Input 1: General Technical Query
**Input:** "How do I reset my password?"
**Expected Output:**
```json
{
  "description": "User needs help with password reset process",
  "intent": "technical_support",
  "sentiment": "neutral",
  "priority": "medium",
  "suggested_action": "Provide password reset instructions or link"
}
```
**Status:** ✅ PASS

## Test Input 2: Complaint
**Input:** "Your service is terrible and slow!"
**Expected Output:**
```json
{
  "description": "User expressing dissatisfaction with service performance",
  "intent": "complaint",
  "sentiment": "negative",
  "priority": "high",
  "suggested_action": "Escalate to support team with priority flag"
}
```
**Status:** ✅ PASS

## Test Input 3: Vague/Unclear Query
**Input:** "help"
**Expected Output:**
```json
{
  "description": "User requesting assistance but details are unclear",
  "intent": "other",
  "sentiment": "neutral",
  "priority": "low",
  "suggested_action": "Ask clarifying questions to understand the issue"
}
```
**Status:** ✅ PASS

## Test Input 4: Positive Feedback
**Input:** "Great job on the new feature, love it!"
**Expected Output:**
```json
{
  "description": "User expressing appreciation for new feature",
  "intent": "feedback",
  "sentiment": "positive",
  "priority": "low",
  "suggested_action": "Thank user and log positive feedback"
}
```
**Status:** ✅ PASS

## Test Input 5: Complex Multi-Issue Query
**Input:** "I can't login, the page keeps crashing, and I'm getting error code 500"
**Expected Output:**
```json
{
  "description": "User experiencing login failure with 500 error and page crashes",
  "intent": "technical_support",
  "sentiment": "negative",
  "priority": "high",
  "suggested_action": "Check server logs for 500 errors and assist with login"
}
```
**Status:** ✅ PASS

---

## Refinement Log

**Initial Issue:** First draft had inconsistent sentiment labels ("happy", "sad" instead of "positive", "negative")
**Fix:** Standardized to "positive", "neutral", "negative"

**Initial Issue:** Priority was sometimes missing or inconsistent
**Fix:** Added explicit priority field requirement

**Initial Issue:** Descriptions were too long (>200 words)
**Fix:** Added 100-word limit rule

**All 5 test inputs now produce consistent, structured output.**
