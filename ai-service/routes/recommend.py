from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import os
import json

recommend_bp = Blueprint('recommend', __name__)


@recommend_bp.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()

    # Validate input
    if not data or 'user_input' not in data:
        return jsonify({'error': 'user_input is required'}), 400

    user_input = data.get('user_input', '').strip()

    if not user_input:
        return jsonify({'error': 'user_input cannot be empty'}), 400

    if len(user_input) > 1000:
        return jsonify({'error': 'user_input exceeds 1000 characters'}), 400

    # Load prompt template
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'recommend.txt')

    try:
        with open(prompt_path, 'r') as f:
            prompt_template = f.read()
    except FileNotFoundError:
        return jsonify({'error': 'Prompt template not found'}), 500

    # Replace placeholder
    prompt = prompt_template.replace('{user_input}', user_input)

    # Call Groq with cache
    from services.groq_client import GroqClient
    cache_service = current_app.config.get('cache_service')
    groq_client = GroqClient(cache_service)
    response = groq_client.generate('recommend', user_input, prompt)

    if not response:
        return jsonify({'error': 'Failed to generate response'}), 500

    # Parse JSON response
    try:
        recommendations = json.loads(response)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON response from AI'}), 500

    # Validate response structure
    if not isinstance(recommendations, list) or len(recommendations) != 3:
        return jsonify({'error': 'Invalid response format: expected array of 3 recommendations'}), 500

    for rec in recommendations:
        if not all(key in rec for key in ['action_type', 'description', 'priority']):
            return jsonify({'error': 'Invalid recommendation format: missing required fields'}), 500

    # Add generated_at timestamp
    result = {
        'recommendations': recommendations,
        'generated_at': datetime.utcnow().isoformat()
    }

    return jsonify(result), 200
