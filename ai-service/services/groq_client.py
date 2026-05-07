import os
import time
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqClient:
    def __init__(self, cache_service=None):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.model = "llama-3.3-70b-versatile"
        self.cache_service = cache_service
        self.timeout = 10  # 10 second timeout for Groq API
    
    def _get_fallback(self, endpoint: str) -> str:
        """Return fallback template with is_fallback: true"""
        fallbacks = {
            'describe': {
                "description": "Unable to process request - AI service temporarily unavailable",
                "intent": "other",
                "sentiment": "neutral",
                "priority": "low",
                "suggested_action": "Retry request or contact support",
                "is_fallback": True
            },
            'recommend': {
                "recommendations": [
                    {
                        "action_type": "retry",
                        "description": "Retry the request as AI service is temporarily unavailable",
                        "priority": "medium"
                    },
                    {
                        "action_type": "contact_support",
                        "description": "Contact support if issue persists",
                        "priority": "low"
                    },
                    {
                        "action_type": "check_status",
                        "description": "Check /health endpoint for service status",
                        "priority": "low"
                    }
                ],
                "is_fallback": True
            },
            'generate_report': {
                "title": "Service Temporarily Unavailable",
                "summary": "Unable to generate report - AI service is temporarily unavailable",
                "overview": "The AI service encountered an error while processing your request. Please retry or contact support.",
                "key_items": ["AI service temporarily unavailable", "Request could not be processed"],
                "recommendations": ["Retry the request", "Check /health endpoint", "Contact support if issue persists"],
                "is_fallback": True
            }
        }
        return json.dumps(fallbacks.get(endpoint, fallbacks['describe']))
    
    def generate(self, endpoint: str, user_input: str, prompt: str) -> str:
        # Check cache first
        if self.cache_service:
            cached_result = self.cache_service.get(endpoint, user_input)
            if cached_result:
                return json.dumps(cached_result)
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that responds in valid JSON format only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                timeout=self.timeout
            )
            result = response.choices[0].message.content
            
            # Strip markdown code blocks if present
            result = result.strip()
            if result.startswith('```json'):
                result = result[7:].strip()
            elif result.startswith('```'):
                result = result[3:].strip()
            if result.endswith('```'):
                result = result[:-3].strip()
            
            # Strip double braces (Groq sometimes returns {{ instead of {)
            if result.startswith('{{'):
                result = result[1:]
            if result.endswith('}}'):
                result = result[:-1]
            
            # Record response time
            duration_ms = (time.time() - start_time) * 1000
            if self.cache_service:
                self.cache_service.record_response_time(duration_ms)
            
            # Check if response time is under 2s target
            if duration_ms > 2000:
                print(f"Warning: Response time {duration_ms}ms exceeds 2s target")
            
            # Cache the result
            if self.cache_service:
                try:
                    parsed = json.loads(result)
                    self.cache_service.set(endpoint, user_input, parsed)
                except:
                    pass
            
            return result
        except Exception as e:
            print(f"Groq API error: {e}")
            # Return fallback template instead of None
            return self._get_fallback(endpoint)
