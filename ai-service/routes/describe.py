from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import os
import json

describe_bp = Blueprint('describe', __name__)

@describe_bp.route('/describe', methods=['POST'])
def describe():
    print("DEBUG: /describe route called")
    data = request.get_json()
    print(f"DEBUG: Received data: {data}")
    
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
    
    # Call Groq with cache
    from services.groq_client import GroqClient
    cache_service = current_app.config.get('cache_service')
    try:
        groq_client = GroqClient(cache_service)
        response = groq_client.generate('describe', user_input, prompt)
    except Exception as e:
        print(f"ERROR in describe: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Groq client error: {str(e)}'}), 500
    
    # Parse JSON response (fallback always returns valid JSON with is_fallback flag)
    try:
        # Strip markdown code blocks if present
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:].strip()
        elif response.startswith('```'):
            response = response[3:].strip()
        if response.endswith('```'):
            response = response[:-3].strip()
        
        # Strip double braces (Groq sometimes returns {{ instead of {)
        if response.startswith('{{'):
            response = response[1:]
        if response.endswith('}}'):
            response = response[:-1]
        
        result = json.loads(response)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Response was: {response[:200]}")
        return jsonify({'error': 'Invalid JSON response from AI'}), 500
    
    # Add generated_at timestamp
    result['generated_at'] = datetime.utcnow().isoformat()
    
    # Return 200 OK even for fallback responses (client checks is_fallback flag)
    return jsonify(result), 200
