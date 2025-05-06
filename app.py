
from flask import Flask, request, jsonify, redirect
import os
import uuid
import ssl
import json
import requests
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
VERIFY_URL = os.getenv("VERIFY_URL", "http://localhost:5000/verify")
TOKENS_FILE = "tokens.json"

RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET")
ZOHO_ACCESS_TOKEN = os.getenv("ZOHO_ACCESS_TOKEN")
ZOHO_API_URL = os.getenv("ZOHO_API_URL")

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")

if not os.path.exists(TOKENS_FILE):
    with open(TOKENS_FILE, 'w') as f:
        json.dump({}, f)

def save_token(email, token):
    with open(TOKENS_FILE, 'r') as f:
        data = json.load(f)
    data[token] = email
    with open(TOKENS_FILE, 'w') as f:
        json.dump(data, f)

def load_email_from_token(token):
    with open(TOKENS_FILE, 'r') as f:
        data = json.load(f)
    return data.get(token)

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    captcha_token = request.form.get("g-recaptcha-response")
    if not email or not captcha_token:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    recaptcha_response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={"secret": RECAPTCHA_SECRET, "response": captcha_token}
    )
    if not recaptcha_response.json().get("success"):
        return jsonify({"status": "error", "message": "Invalid captcha"}), 403

    token = str(uuid.uuid4())
    save_token(email, token)

    try:
        msg = EmailMessage()
        msg["Subject"] = "Please verify your email"
        msg["From"] = SMTP_EMAIL
        msg["To"] = email
        msg.set_content(f"Click to confirm: {VERIFY_URL}?token={token}")

        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "ok", "message": "Check your email to verify."})

@app.route("/verify")
def verify():
    token = request.args.get("token")
    email = load_email_from_token(token)
    if not email:
        return "Invalid or expired token", 400

    headers = {"Authorization": f"Zoho-oauthtoken {ZOHO_ACCESS_TOKEN}"}
    data = {"data": [{"Email": email, "Lead_Source": "Landing Page"}]}
    response = requests.post(ZOHO_API_URL, headers=headers, json=data)

    return "Email verified and added!" if response.ok else f"Error: {response.text}"

if __name__ == "__main__":
    app.run(debug=True, port=5000)
