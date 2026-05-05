from flask import Blueprint, request, jsonify
from datetime import datetime
import os
import json

generate_report_bp = Blueprint('generate_report', __name__)


@generate_report_bp.route('/generate-report', methods=['POST'])
def generate_report():
    data = request.get_json()

    # Validate input
    if not data or 'user_input' not in data:
        return jsonify({'error': 'user_input is required'}), 400

    user_input = data.get('user_input', '').strip()

    if not user_input:
        return jsonify({'error': 'user_input cannot be empty'}), 400

    if len(user_input) > 2000:
        return jsonify({'error': 'user_input exceeds 2000 characters'}), 400

    # Load prompt template
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'generate_report.txt')

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
        report = json.loads(response)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON response from AI'}), 500

    # Validate required fields
    required_fields = ['title', 'summary', 'overview', 'key_items', 'recommendations']
    for field in required_fields:
        if field not in report:
            return jsonify({'error': f'Missing required field: {field}'}), 500

    # Validate arrays
    if not isinstance(report['key_items'], list):
        return jsonify({'error': 'key_items must be an array'}), 500
    if not isinstance(report['recommendations'], list):
        return jsonify({'error': 'recommendations must be an array'}), 500

    # Add generated_at timestamp
    report['generated_at'] = datetime.utcnow().isoformat()

    return jsonify(report), 200
