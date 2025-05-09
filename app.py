from flask import Flask, request, jsonify, send_from_directory
import os
import requests

# If using Render Secrets, load from /etc/secrets
def get_env(key):
    paths = [
        f"/etc/secrets/{key}",   # Render secrets
        f".env"                  # Local fallback
    ]
    for path in paths:
        if os.path.exists(path):
            with open(path) as f:
                return f.read().strip()
    return os.getenv(key)

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

def get_access_token():
    refresh_token = get_env("ZOHO_REFRESH_TOKEN")
    client_id = get_env("ZOHO_CLIENT_ID")
    client_secret = get_env("ZOHO_CLIENT_SECRET")

    token_url = "https://accounts.zoho.eu/oauth/v2/token"
    params = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }

    response = requests.post(token_url, params=params)

    if response.ok:
        return response.json().get("access_token"), None
    else:
        return None, response.text

@app.route('/verify', methods=["GET", "POST"])
def verify():
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Missing token"}), 400

    access_token, error = get_access_token()
    if not access_token:
        return jsonify({"error": "Failed to fetch Zoho token", "details": error}), 500

    zoho_url = get_env("ZOHO_API_URL")
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
        return jsonify({"message": "Lead added successfully!"})
    else:
        return jsonify({"error": "Zoho CRM error", "details": response.text}), 500

if __name__ == '__main__':
    app.run()
