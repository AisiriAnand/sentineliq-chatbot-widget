#!/usr/bin/env python3
"""
Run all prompts against 30 demo records
Generates demo_outputs.json with all results
Run: python scripts/run_demo.py
"""

import sys
import os
import json
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests

# API base URL
BASE_URL = os.getenv('AI_SERVICE_URL', 'http://localhost:5000')

# 30 Demo Records - Real user queries
DEMO_RECORDS = [
    # Account Issues (5)
    "I forgot my password and can't log in to my account",
    "My account got locked after trying wrong password multiple times",
    "How do I reset my password? I forgot it",
    "Can't access my account - says it's suspended",
    "Need to unlock my account urgently",
    
    # Billing Issues (5)
    "There's a charge of $299 on my card I didn't authorize",
    "My invoice shows double billing for last month",
    "How do I upgrade from free to pro plan?",
    "I want to cancel my subscription and get refund",
    "Billing dispute - charged twice for same service",
    
    # Technical Issues (5)
    "API keeps returning 500 error when I make requests",
    "Integration failing with rate limit exceeded message",
    "Getting error 429 - too many requests",
    "My API key stopped working suddenly",
    "Server error when trying to export data",
    
    # Privacy/GDPR (5)
    "I want to delete all my data from your system",
    "How can I export my personal data?",
    "Requesting complete account deletion under GDPR",
    "Need my data exported in JSON format",
    "Delete my account and all associated data",
    
    # Security (5)
    "I see suspicious login from unknown device",
    "Someone accessed my account without permission",
    "How to enable two-factor authentication?",
    "Getting alerts about suspicious activity",
    "Need to secure my account immediately",
    
    # General/Misc (5)
    "What are your business hours?",
    "How do I contact sales team?",
    "Need help setting up my first integration",
    "Documentation link for API reference?",
    "Do you offer enterprise pricing?"
]

def call_endpoint(endpoint, user_input, retries=2):
    """Call AI service endpoint with retry logic"""
    url = f"{BASE_URL}/{endpoint}"
    payload = {"user_input": user_input}
    
    for attempt in range(retries + 1):
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": 200,
                    "data": response.json()
                }
            elif response.status_code == 429:
                # Rate limited, wait and retry
                time.sleep(1)
                continue
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
        except requests.exceptions.Timeout:
            if attempt < retries:
                time.sleep(1)
                continue
            return {
                "success": False,
                "status_code": None,
                "error": "Request timeout"
            }
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
                continue
            return {
                "success": False,
                "status_code": None,
                "error": str(e)
            }
    
    return {
        "success": False,
        "status_code": None,
        "error": "Max retries exceeded"
    }

def run_demo():
    """Run all prompts against 30 demo records"""
    
    print("=" * 70)
    print("RUNNING DEMO: All prompts against 30 records")
    print(f"API URL: {BASE_URL}")
    print("=" * 70)
    
    # Check health first
    print("\n[1/4] Checking service health...")
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code == 200:
            health_data = health.json()
            print(f"  ✓ Service healthy")
            print(f"    Model: {health_data.get('model', 'N/A')}")
            print(f"    Redis: {health_data.get('redis_status', 'N/A')}")
            print(f"    Embedding: {health_data.get('embedding_status', 'N/A')}")
        else:
            print(f"  ✗ Health check failed: {health.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Cannot connect to service: {e}")
        print(f"    Make sure the AI service is running on {BASE_URL}")
        return False
    
    # Run tests
    results = {
        "metadata": {
            "total_records": len(DEMO_RECORDS),
            "endpoints_tested": ["describe", "recommend", "generate_report"],
            "base_url": BASE_URL
        },
        "summary": {
            "describe": {"success": 0, "failed": 0, "fallback": 0},
            "recommend": {"success": 0, "failed": 0, "fallback": 0},
            "generate-report": {"success": 0, "failed": 0, "fallback": 0}
        },
        "records": []
    }
    
    endpoints = ["describe", "recommend", "generate-report"]
    
    for i, user_input in enumerate(DEMO_RECORDS, 1):
        print(f"\n[{i}/{len(DEMO_RECORDS)}] Testing: '{user_input[:50]}...'")
        
        record_result = {
            "record_id": i,
            "user_input": user_input,
            "responses": {}
        }
        
        for endpoint in endpoints:
            print(f"  Calling /{endpoint}...", end=" ")
            
            start_time = time.time()
            response = call_endpoint(endpoint, user_input)
            duration = round((time.time() - start_time) * 1000, 2)
            
            # Check if fallback
            is_fallback = False
            if response["success"]:
                data = response["data"]
                is_fallback = data.get("is_fallback", False)
            
            # Update counters
            if response["success"]:
                if is_fallback:
                    results["summary"][endpoint]["fallback"] += 1
                    print(f"✓ FALLBACK ({duration}ms)")
                else:
                    results["summary"][endpoint]["success"] += 1
                    print(f"✓ OK ({duration}ms)")
            else:
                results["summary"][endpoint]["failed"] += 1
                print(f"✗ FAIL ({duration}ms) - {response.get('error', 'Unknown')}")
            
            record_result["responses"][endpoint] = {
                "success": response["success"],
                "duration_ms": duration,
                "is_fallback": is_fallback,
                "status_code": response.get("status_code"),
                "error": response.get("error"),
                "data": response.get("data") if response["success"] else None
            }
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        results["records"].append(record_result)
    
    # Save results
    output_file = "demo_outputs.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 70)
    print("DEMO COMPLETE - SUMMARY")
    print("=" * 70)
    
    for endpoint, stats in results["summary"].items():
        total = stats["success"] + stats["failed"] + stats["fallback"]
        success_rate = (stats["success"] / total * 100) if total > 0 else 0
        print(f"\n/{endpoint}:")
        print(f"  Success: {stats['success']}/{total} ({success_rate:.1f}%)")
        print(f"  Fallback: {stats['fallback']}/{total}")
        print(f"  Failed: {stats['failed']}/{total}")
    
    print(f"\nOutput saved to: {output_file}")
    print("=" * 70)
    
    # All outputs should be demo-ready (success or fallback, no failures)
    total_failures = sum(s["failed"] for s in results["summary"].values())
    return total_failures == 0

if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)
