from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Load environment variables
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)

# Health check
@app.route('/')
def home():
    return '✅ Backend is running!'

# Zoho lead verification route
@app.route('/verify')
def verify():
    token = request.args.get("token")
    
    def load_email_from_token(tkn):
        # Replace with secure logic if token is encoded
        return tkn  # assuming token = email for now

    email = load_email_from_token(token)
    if not email:
        return jsonify({"error": "Invalid or expired token"}), 400

    zoho_token = os.getenv("ZOHO_ACCESS_TOKEN")
    zoho_url = os.getenv("ZOHO_API_URL")

    if not zoho_token or not zoho_url:
        return jsonify({"error": "Missing Zoho API configuration"}), 500

    headers = {
        "Authorization": f"Zoho-oauthtoken {zoho_token}"
    }
    data = {
        "data": [{"Email": email, "Lead_Source": "Landing Page"}]
    }

    try:
        response = requests.post(zoho_url, headers=headers, json=data)
        if response.ok:
            return jsonify({"message": "Email verified and added!"})
        else:
            return jsonify({"error": response.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# No app.run() block - Render uses gunicorn
