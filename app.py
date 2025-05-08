from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Simple health check route
@app.route('/')
def home():
    return 'Backend is running!'

# Verification route
@app.route('/verify')
def verify():
    token = request.args.get("token")
    
    def load_email_from_token(tkn):
        # Replace with actual logic to decode the token if needed
        return tkn  # assuming token is email for simplicity

    email = load_email_from_token(token)
    if not email:
        return "Invalid or expired token", 400

    headers = {
        "Authorization": f"Zoho-oauthtoken {os.getenv('ZOHO_ACCESS_TOKEN')}"
    }
    data = {
        "data": [{"Email": email, "Lead_Source": "Landing Page"}]
    }
    response = requests.post(os.getenv('ZOHO_API_URL'), headers=headers, json=data)

    if response.ok:
        return "Email verified and added!"
    else:
        return f"Error: {response.text}", 500

if __name__ == '__main__':
    app.run(debug=True)
