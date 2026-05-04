from flask import Flask
from routes.describe import describe_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.register_blueprint(describe_bp)


@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy'}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
