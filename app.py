from flask import Flask, request, jsonify, send_from_directory
import os
import requests
from dotenv import load_dotenv

# Load .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))

# Point Flask to parent directory for static assets
app = Flask(__name__, static_folder=os.path.abspath(os.path.join(basedir, '..')), static_url_path='')

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/verify')
def verify():
    token = request.args.get("token")

    def load_email_from_token(tkn):
        return tkn  # still assuming raw email token

    email = load_email_from_token(token)
    if not email:
        return jsonify({"error": "Invalid or expired token"}), 400

    access_token = os.getenv("ZOHO_ACCESS_TOKEN")
    api_url = os.getenv("ZOHO_API_URL")

    if not access_token or not api_url:
        return jsonify({"error": "Missing Zoho API configuration"}), 500

    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    data = {"data": [{"Email": email, "Lead_Source": "Landing Page"}]}

    try:
        response = requests.post(api_url, headers=headers, json=data)
        if response.ok:
            return jsonify({"message": "Email verified and added!"})
        else:
            return jsonify({"error": response.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
