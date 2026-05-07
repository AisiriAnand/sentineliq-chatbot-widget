#!/usr/bin/env python3
"""
Seed ChromaDB with 10 domain knowledge documents
Run: python scripts/seed_chroma.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.chroma_service import ChromaService
from services.embedding_service import EmbeddingService

def seed_domain_knowledge():
    """Seed ChromaDB with 10 domain knowledge documents"""
    
    print("=" * 60)
    print("SEEDING CHROMADB WITH DOMAIN KNOWLEDGE")
    print("=" * 60)
    
    # Initialize services
    embedding_service = EmbeddingService()
    embedding_service.load_model()
    
    chroma = ChromaService(embedding_service)
    
    # 10 Domain Knowledge Documents
    documents = [
        {
            "id": "doc_001",
            "text": "Password Reset: To reset your password, click 'Forgot Password' on the login page. Enter your registered email address and click 'Send Reset Link'. Check your email inbox for the reset link which expires in 24 hours. Click the link and create a new password with at least 8 characters including uppercase, lowercase, number, and special character.",
            "metadata": {"category": "account", "type": "faq", "priority": "high"}
        },
        {
            "id": "doc_002",
            "text": "Account Locked: If your account is locked due to multiple failed login attempts, wait 30 minutes before trying again. Alternatively, contact support with your account ID for immediate unlock. Have your registered email and phone number ready for verification.",
            "metadata": {"category": "account", "type": "faq", "priority": "high"}
        },
        {
            "id": "doc_003",
            "text": "Billing Dispute: For billing discrepancies, gather your invoice number, transaction date, and amount in question. Submit a dispute ticket through the billing portal within 30 days of the charge. Resolution typically takes 5-7 business days. Refunds are processed to the original payment method.",
            "metadata": {"category": "billing", "type": "faq", "priority": "medium"}
        },
        {
            "id": "doc_004",
            "text": "Subscription Upgrade: To upgrade your subscription, go to Account Settings > Subscription. Select your desired plan and click 'Upgrade'. The prorated difference will be charged immediately. Features become available instantly. Downgrades take effect at the next billing cycle.",
            "metadata": {"category": "billing", "type": "faq", "priority": "low"}
        },
        {
            "id": "doc_005",
            "text": "API Rate Limits: Free tier: 100 requests/hour. Pro tier: 1000 requests/hour. Enterprise: 10000 requests/hour. Rate limits reset at the top of each hour. If you exceed limits, you'll receive HTTP 429. Contact sales for custom limits.",
            "metadata": {"category": "technical", "type": "documentation", "priority": "medium"}
        },
        {
            "id": "doc_006",
            "text": "Integration Error 500: Internal server errors during API integration are typically temporary. Retry the request with exponential backoff (1s, 2s, 4s, 8s). If errors persist beyond 10 minutes, check our status page or contact support with your request ID from the response headers.",
            "metadata": {"category": "technical", "type": "troubleshooting", "priority": "high"}
        },
        {
            "id": "doc_007",
            "text": "Data Export: To export your data, navigate to Settings > Data Privacy > Export Data. Select data types (profile, activity, logs) and format (JSON or CSV). Export requests are processed within 48 hours. You'll receive an email with a secure download link valid for 7 days.",
            "metadata": {"category": "privacy", "type": "faq", "priority": "low"}
        },
        {
            "id": "doc_008",
            "text": "GDPR Data Deletion: Under GDPR, you can request complete account deletion. This removes all personal data within 30 days. Some anonymized usage data may be retained for analytics. Submit a deletion request via Settings > Data Privacy > Delete Account. This action is irreversible.",
            "metadata": {"category": "privacy", "type": "compliance", "priority": "high"}
        },
        {
            "id": "doc_009",
            "text": "Two-Factor Authentication: Enable 2FA in Security Settings. We support TOTP apps (Google Authenticator, Authy) and SMS. After setup, you'll need both password and verification code to login. Recovery codes are provided - store them securely. Disable 2FA requires email verification.",
            "metadata": {"category": "security", "type": "faq", "priority": "high"}
        },
        {
            "id": "doc_010",
            "text": "Suspicious Activity: If you notice unrecognized logins or activity, immediately change your password and enable 2FA. Check active sessions in Security Settings and revoke unknown devices. Contact support to review account logs and enable additional monitoring.",
            "metadata": {"category": "security", "type": "urgent", "priority": "high"}
        }
    ]
    
    # Add documents to ChromaDB
    success_count = 0
    for doc in documents:
        print(f"\nAdding: {doc['id']} - {doc['metadata']['category']}")
        success = chroma.add_document(
            doc_id=doc['id'],
            text=doc['text'],
            metadata=doc['metadata']
        )
        if success:
            success_count += 1
            print(f"  ✓ Added successfully")
        else:
            print(f"  ✗ Failed to add")
    
    # Persist to disk
    chroma.persist()
    
    print("\n" + "=" * 60)
    print(f"SEEDING COMPLETE: {success_count}/{len(documents)} documents added")
    print(f"Total documents in collection: {chroma.get_collection_count()}")
    print("=" * 60)
    
    # Test search
    print("\nTesting search functionality:")
    test_queries = [
        "how do I reset my password",
        "my account is locked",
        "billing issue with my invoice"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = chroma.search(query, n_results=2)
        for i, result in enumerate(results):
            print(f"  {i+1}. {result['id']} (dist: {result['distance']:.4f})")
    
    return success_count == len(documents)

if __name__ == "__main__":
    success = seed_domain_knowledge()
    sys.exit(0 if success else 1)
