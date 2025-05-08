from flask import Flask, request, jsonify
import os
import requests

# Dummy token decoder (replace with actual secure logic)
def load_email_from_token(token):
    # In production, decode and validate the token securely
    token_map = {
        "test123": "testuser@fun-bet.me",
        "abc456": "abc@fun-bet.me"
    }
    return token_map.get(token)

app = Flask(__name__)

@app.route('/')
def home():
    return "Backend is running!"

@app.route('/verify')
def verify():
    token = request.args.get("token")
    email = load_email_from_token(token)

    if not email:
        return jsonify({"status": "error", "message": "Invalid or expired token"}), 400

    headers = {
        "Authorization": f"Zoho-oauthtoken {os.environ.get('ZOHO_ACCESS_TOKEN')}"
    }
    data = {
        "data": [
            {
                "Email": email,
                "Lead_Source": "Landing Page"
            }
        ]
    }

    response = requests.post(os.environ.get("ZOHO_API_URL"), headers=headers, json=data)

    if response.ok:
        return jsonify({"status": "ok", "message": "Email verified and added!"})
    else:
        return jsonify({"status": "error", "message": f"Error from Zoho: {response.text}"}), 500
