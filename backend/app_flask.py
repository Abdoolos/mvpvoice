"""
Simple Flask app for testing Render deployment
Designer: Abdullah Alawiss
"""

from flask import Flask, jsonify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "AI Callcenter Agent MVP - Flask Test",
        "status": "running",
        "designer": "Abdullah Alawiss"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "ai-callcenter-backend",
        "version": "1.0.0"
    })

@app.route('/api/v1/test')
def api_test():
    return jsonify({
        "message": "API endpoint working",
        "framework": "Flask",
        "python_version": "3.13"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
