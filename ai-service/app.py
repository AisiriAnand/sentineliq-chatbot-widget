from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.generate_report import generate_report_bp
from services.cache_service import CacheService
from services.embedding_service import EmbeddingService
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Initialize rate limiter for ZAP active scan protection
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute", "1000 per hour"],
    storage_uri="memory://"
)

# Initialize cache service
app.config['cache_service'] = CacheService()

# Pre-load sentence-transformers model at startup
print("Initializing services...")
embedding_service = EmbeddingService()
embedding_service.load_model()
app.config['embedding_service'] = embedding_service

# Track start time for uptime
app.config['start_time'] = datetime.utcnow()

app.register_blueprint(describe_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(generate_report_bp)


@app.after_request
def add_security_headers(response):
    """Add security headers to fix OWASP ZAP findings"""
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    # XSS Protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Content Security Policy
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
    # Strict Transport Security (HTTPS only)
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Permissions Policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    # CORS - Restrictive for API
    response.headers['Access-Control-Allow-Origin'] = os.getenv('ALLOWED_ORIGIN', '*')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    # Cache Control for sensitive data
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.before_request
def check_content_type():
    """Validate Content-Type for POST requests"""
    if request.method == 'POST':
        content_type = request.content_type or ''
        if not content_type.startswith('application/json'):
            return {'error': 'Content-Type must be application/json'}, 415


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    return {'error': 'Rate limit exceeded. Too many requests.'}, 429


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return {'error': 'Internal server error'}, 500


@app.route('/health', methods=['GET'])
def health_check():
    cache_service = app.config.get('cache_service')
    embedding_service = app.config.get('embedding_service')
    start_time = app.config.get('start_time')
    
    # Calculate uptime
    uptime_seconds = (datetime.utcnow() - start_time).total_seconds()
    uptime_hours = uptime_seconds / 3600
    
    # Get average response time from cache stats
    avg_response_time = cache_service.get_avg_response_time() if cache_service else 0
    
    # Check Redis connection
    redis_status = 'connected' if cache_service and cache_service.is_connected() else 'disconnected'
    
    # Check embedding service
    embedding_status = 'loaded' if embedding_service and embedding_service.is_loaded() else 'not_loaded'
    
    return {
        'status': 'healthy',
        'service': 'sentineliq-ai',
        'model': 'llama-3.3-70b-versatile',
        'version': '1.0.0',
        'avg_response_time_ms': round(avg_response_time, 2),
        'uptime_hours': round(uptime_hours, 2),
        'redis_status': redis_status,
        'embedding_status': embedding_status,
        'embedding_model': os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
        'timestamp': datetime.utcnow().isoformat()
    }, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
