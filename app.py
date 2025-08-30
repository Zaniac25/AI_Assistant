import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

# Load API Key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return [{"role": "system", "content": "You are a helpful and friendly AI chatbot."}]
    return [{"role": "system", "content": "You are a helpful and friendly AI chatbot."}]

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    chat_history = load_history()

    # Add user message
    chat_history.append({"role": "user", "content": user_message})

    try:
        conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([conversation])
        bot_reply = response.text.strip()

        chat_history.append({"role": "assistant", "content": bot_reply})
        save_history(chat_history)

        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"reply": f"⚠️ Error: {e}"})

if __name__ == "__main__":
    app.run(debug=True)
