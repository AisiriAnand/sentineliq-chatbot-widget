from flask import Blueprint, request, jsonify
from datetime import datetime
import os
import json

describe_bp = Blueprint('describe', __name__)

@describe_bp.route('/describe', methods=['POST'])
def describe():
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
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'describe.txt')
    
    try:
        with open(prompt_path, 'r') as f:
            prompt_template = f.read()
    except FileNotFoundError:
        return jsonify({'error': 'Prompt template not found'}), 500
    
    # Replace placeholder
    prompt = prompt_template.replace('{user_input}', user_input)
    
    # Call Groq
    from services.groq_client import GroqClient
    groq_client = GroqClient()
    response = groq_client.generate(prompt)
    
    if not response:
        return jsonify({'error': 'Failed to generate response'}), 500
    
    # Parse JSON response
    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON response from AI'}), 500
    
    # Add generated_at timestamp
    result['generated_at'] = datetime.utcnow().isoformat()
    
    return jsonify(result), 200
