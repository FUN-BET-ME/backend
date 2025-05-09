from flask import Flask, request, jsonify, send_from_directory
import os
import requests
from dotenv import load_dotenv

# ✅ Load environment from Render Secret Files path
load_dotenv("/etc/secrets/.env")

app = Flask(__name__)

# Serve index.html
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# Serve static files like logo, CSS, etc.
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# Get Zoho token from refresh
def get_access_token():
    refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
    client_id = os.getenv("ZOHO_CLIENT_ID")
    client_secret = os.getenv("ZOHO_CLIENT_SECRET")

    token_url = "https://accounts.zoho.eu/oauth/v2/token"

    response = requests.post(token_url, params={
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    })

    if response.ok:
        return response.json().get("access_token"), None
    else:
        return None, response.text  # debug details

# Verify route
@app.route('/verify', methods=["GET", "POST"])
def verify():
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Missing or invalid token"}), 400

    access_token, error_details = get_access_token()
    if not access_token:
        return jsonify({
            "error": "Failed to fetch Zoho token",
            "details": error_details
        }), 500

    zoho_url = os.getenv("ZOHO_API_URL")
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    data = {
        "data": [{
            "Email": token,
            "Lead_Source": "Landing Page"
        }]
    }

    response = requests.post(zoho_url, headers=headers, json=data)
    if response.ok:
        return jsonify({"message": "Lead added successfully"})
    else:
        return jsonify({"error": "Zoho API error", "details": response.text}), 500

if __name__ == "__main__":
    app.run()
