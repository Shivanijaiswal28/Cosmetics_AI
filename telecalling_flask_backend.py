#!/usr/bin/env python3
"""
Outbound tele-calling backend for "SHIVANI'S Cosmetics Advisor AI"
Structured flow:
1. Ask product category
2. Ask budget
3. Fetch from DB
4. Give final answer
"""

from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
import os
import mysql.connector

# ---------- Configuration ----------
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
USER_PHONE_NUMBER = os.getenv("USER_PHONE_NUMBER")

DB_PASSWORD = os.getenv("DB_PASSWORD", "shivani28")

# Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# DB connect
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password=DB_PASSWORD,
    database="cosmetics_db"
)
cursor = db.cursor(dictionary=True)

# ---------- Global Memory ----------
conversation_stage = 0
user_preferences = {"category": None, "budget": None}

def reset_conversation():
    global conversation_stage, user_preferences
    conversation_stage = 0
    user_preferences = {"category": None, "budget": None}

# ---------- DB Helper ----------
def fetch_products(category=None, budget=None):
    query = "SELECT name, price, category FROM products WHERE stock > 0"
    params = []

    if category:
        query += " AND category=%s"
        params.append(category)
    if budget:
        if budget.lower() == "low":
            query += " AND price < 500"
        elif budget.lower() == "medium":
            query += " AND price BETWEEN 500 AND 1500"
        elif budget.lower() == "premium":
            query += " AND price > 1500"

    cursor.execute(query, tuple(params))
    return cursor.fetchall()

# ---------- Flask ----------
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Cosmetics Advisor AI ✅ Running"

@app.route("/make_call", methods=["GET"])
def make_call():
    try:
        reset_conversation()
        call = twilio_client.calls.create(
            to=USER_PHONE_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            url="https://26e7fe1559c2.ngrok-free.app/voice"
        )
        return f"Calling {USER_PHONE_NUMBER}... SID: {call.sid}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/voice", methods=["POST"])
def voice():
    global conversation_stage
    reset_conversation()

    resp = VoiceResponse()
    gather = Gather(input="speech", action="https://26e7fe1559c2.ngrok-free.app/process", method="POST", timeout=5)
    gather.say("Namaste! Welcome to Shivani's Cosmetics Advisor. Aap kis type ka product dekhna chahte ho? Example lipstick, cream, foundation.", voice="alice", language="en-IN")
    resp.append(gather)

    conversation_stage = 1
    return str(resp)

@app.route("/process", methods=["POST"])
def process():
    global conversation_stage, user_preferences

    user_text = request.form.get("SpeechResult")
    print(f"Stage {conversation_stage} | Caller said:", user_text)

    resp = VoiceResponse()

    if not user_text:
        resp.say("Sorry, I could not understand. Please repeat.", voice="alice", language="en-IN")
        resp.redirect("/voice")
        return str(resp)

    # ---- Stage 1: Ask category ----
    if conversation_stage == 1:
        user_preferences["category"] = user_text.lower()
        conversation_stage = 2
        resp.say(f"Thik hai, aapko {user_text} chahiye. Aapka budget kya hai? Low, Medium, ya Premium?", voice="alice", language="en-IN")
        gather = Gather(input="speech", action="https://26e7fe1559c2.ngrok-free.app/process", method="POST", timeout=5)
        resp.append(gather)
        return str(resp)

    # ---- Stage 2: Ask budget ----
    elif conversation_stage == 2:
        user_preferences["budget"] = user_text.lower()
        conversation_stage = 3

        # Fetch products from DB
        products = fetch_products(user_preferences["category"], user_preferences["budget"])

        if products:
            product_list = ", ".join([f"{p['name']} {p['price']} rupees" for p in products[:5]])
            resp.say(f"Aapke liye ye products mil gaye: {product_list}.", voice="alice", language="en-IN")
        else:
            resp.say("Sorry, is budget me koi product available nahi hai.", voice="alice", language="en-IN")

        resp.say("Dhanyavaad! Aapse baat karke accha laga. Goodbye.", voice="alice", language="en-IN")
        return str(resp)

    # Default fallback
    else:
        resp.say("Sorry, kuch problem ho gayi. Call end kar raha hu.", voice="alice", language="en-IN")
        return str(resp)

@app.route("/reset", methods=["POST"])
def reset():
    reset_conversation()
    return "Conversation reset ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
