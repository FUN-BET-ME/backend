from flask import Flask, request, jsonify, send_from_directory
import os
import requests
from dotenv import load_dotenv

# Load .env from project root
basedir = os.path.abspath(os.path.dirname(__file__))
rootdir = os.path.abspath(os.path.join(basedir, '..'))
load_dotenv(os.path.join(rootdir, '.env'))

app = Flask(__name__)

# Serve index.html from root directory
@app.route('/')
def serve_index():
    return send_from_directory(rootdir, 'index.html')

# Serve static files from root (e.g. logo.png, styles.css)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(rootdir, filename)

# Zoho lead verification route
@app.route('/verify')
def verify():
    token = request.args.get("token")

    def load_email_from_token(tkn):
        return tkn  # replace with real decoding logic if needed

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
