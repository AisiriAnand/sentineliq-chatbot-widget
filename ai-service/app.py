from flask import Flask
from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.generate_report import generate_report_bp
from services.cache_service import CacheService
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Initialize cache service
app.config['cache_service'] = CacheService()

# Track start time for uptime
app.config['start_time'] = datetime.utcnow()

app.register_blueprint(describe_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(generate_report_bp)


@app.route('/health', methods=['GET'])
def health_check():
    cache_service = app.config.get('cache_service')
    start_time = app.config.get('start_time')
    
    # Calculate uptime
    uptime_seconds = (datetime.utcnow() - start_time).total_seconds()
    uptime_hours = uptime_seconds / 3600
    
    # Get average response time from cache stats
    avg_response_time = cache_service.get_avg_response_time() if cache_service else 0
    
    # Check Redis connection
    redis_status = 'connected' if cache_service and cache_service.is_connected() else 'disconnected'
    
    return {
        'status': 'healthy',
        'service': 'sentineliq-ai',
        'model': 'llama-3.3-70b-versatile',
        'version': '1.0.0',
        'avg_response_time_ms': round(avg_response_time, 2),
        'uptime_hours': round(uptime_hours, 2),
        'redis_status': redis_status,
        'timestamp': datetime.utcnow().isoformat()
    }, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
