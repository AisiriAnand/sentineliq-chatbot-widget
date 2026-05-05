import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqClient:
    def __init__(self, cache_service=None):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.model = "llama-3.3-70b-versatile"
        self.cache_service = cache_service
    
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
                max_tokens=500
            )
            result = response.choices[0].message.content
            
            # Record response time
            duration_ms = (time.time() - start_time) * 1000
            if self.cache_service:
                self.cache_service.record_response_time(duration_ms)
            
            # Cache the result
            if self.cache_service:
                try:
                    import json
                    parsed = json.loads(result)
                    self.cache_service.set(endpoint, user_input, parsed)
                except:
                    pass
            
            return result
        except Exception as e:
            print(f"Groq API error: {e}")
            return None
