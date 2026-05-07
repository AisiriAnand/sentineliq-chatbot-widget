#!/usr/bin/env python3
"""Diagnose what's wrong with the AI service"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("=" * 60)
print("DIAGNOSTIC SCRIPT")
print("=" * 60)

# Test 1: Check .env file
print("\n[1/5] Checking .env file...")
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    print("  ✓ .env file exists")
    with open(env_path) as f:
        content = f.read()
        if 'GROQ_API_KEY=' in content:
            print("  ✓ GROQ_API_KEY found in .env")
        else:
            print("  ✗ GROQ_API_KEY not found in .env")
else:
    print("  ✗ .env file NOT FOUND")
    print("  You MUST create .env file with your API key")

# Test 2: Check prompt files
print("\n[2/5] Checking prompt templates...")
prompts_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
for prompt_file in ['describe.txt', 'recommend.txt', 'generate_report.txt']:
    path = os.path.join(prompts_dir, prompt_file)
    if os.path.exists(path):
        print(f"  ✓ {prompt_file}")
    else:
        print(f"  ✗ {prompt_file} MISSING")

# Test 3: Test Groq API directly
print("\n[3/5] Testing Groq API...")
try:
    from groq import Groq
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("  ✗ GROQ_API_KEY not set in environment")
    else:
        print(f"  ✓ API key found: {api_key[:10]}...")
        try:
            client = Groq(api_key=api_key)
            print("  ✓ Groq client created")
            
            # Test API call
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'API is working' in JSON format like {\"status\": \"ok\"}"}
                ],
                temperature=0.3,
                max_tokens=100
            )
            result = response.choices[0].message.content
            print(f"  ✓ API call successful")
            print(f"  Response: {result}")
        except Exception as e:
            print(f"  ✗ API call failed: {e}")
except ImportError:
    print("  ✗ groq package not installed")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 4: Test Flask app import
print("\n[4/5] Testing Flask app import...")
try:
    import flask
    print(f"  ✓ Flask installed: {flask.__version__}")
except:
    print("  ✗ Flask not installed")

# Test 5: Test routes import
print("\n[5/5] Testing routes...")
try:
    from routes.describe import describe_bp
    print("  ✓ describe route imports")
except Exception as e:
    print(f"  ✗ describe route failed: {e}")

try:
    from routes.recommend import recommend_bp
    print("  ✓ recommend route imports")
except Exception as e:
    print(f"  ✗ recommend route failed: {e}")

try:
    from routes.generate_report import generate_report_bp
    print("  ✓ generate_report route imports")
except Exception as e:
    print(f"  ✗ generate_report route failed: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
