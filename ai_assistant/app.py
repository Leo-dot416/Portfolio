import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "salon.db"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a helpful AI assistant for a hair salon.
Answer questions about services, appointments, and salon guidance clearly and politely.
If you do not know something, say so instead of making it up.
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_faq_answer(user_message):
    message = user_message.lower()

    keyword_map = {
        "hours": ["hour", "open", "opening", "close", "closing", "time"],
        "booking": ["appointment", "book", "booking", "walk in", "walk-in", "schedule"],
        "policy": ["cancel", "cancellation", "refund", "reschedule", "policy"],
        "consultation": ["consultation", "consult", "consults"],
    }

    conn = get_connection()
    try:
        rows = conn.execute("SELECT question, answer, category FROM faqs").fetchall()
        for row in rows:
            question = (row["question"] or "").lower()
            category = (row["category"] or "").lower()

            if question in message or category in message:
                return row["answer"]

            for keywords in keyword_map.values():
                if any(keyword in message for keyword in keywords) and category in keywords:
                    return row["answer"]
    finally:
        conn.close()

    return None


def get_services_text():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT name, description, duration_minutes, price FROM services"
        ).fetchall()

        if not rows:
            return None

        lines = []
        for row in rows:
            lines.append(
                f"{row['name']} - ${row['price']:.2f} - {row['duration_minutes']} min"
            )
            if row["description"]:
                lines.append(f"  {row['description']}")

        return "\n".join(lines)
    finally:
        conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please send a message."}), 400

    faq_answer = get_faq_answer(user_message)
    if faq_answer:
        return jsonify({"reply": faq_answer})

    lowered = user_message.lower()
    if any(word in lowered for word in ["service", "price", "cost", "menu", "offer"]):
        services_text = get_services_text()
        if services_text:
            return jsonify({"reply": f"Here are our services:\n\n{services_text}"})

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        return jsonify({"reply": response.output_text})

    except Exception as error:
        return jsonify({"reply": f"OpenAI error: {error}"}), 500


if __name__ == "__main__":
    app.run(debug=True)