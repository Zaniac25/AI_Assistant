import os
import random
import json
import google.generativeai as genai
from dotenv import load_dotenv
from prompts import casual_chat_prompts, info_prompts, recommendation_prompts

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

HISTORY_FILE = "chat_history.json"

def load_history():
    """Load chat history from file if exists, else start fresh"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = f.read().strip()
                if not data:
                    raise ValueError("Empty file")
                return json.loads(data)
        except Exception:
            return [{"role": "system", "content": "You are a helpful and friendly AI chatbot."}]
    else:
        return [{"role": "system", "content": "You are a helpful and friendly AI chatbot."}]

def save_history(chat_history):
    """Save chat history to file"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

def get_response(user_input, category, chat_history):
    # Pick a random prompt variation
    if category == "1":
        prompt = random.choice(casual_chat_prompts).format(user_input=user_input)
    elif category == "2":
        prompt = random.choice(info_prompts).format(user_input=user_input)
    elif category == "3":
        prompt = random.choice(recommendation_prompts).format(user_input=user_input)
    else:
        return "Invalid choice.", chat_history

    # Add user input to history
    chat_history.append({"role": "user", "content": prompt})

    try:
        # Convert chat history into plain conversation text
        conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])

        # Use Gemini text model
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([conversation])

        bot_reply = response.text.strip()

        # Add assistant reply to history
        chat_history.append({"role": "assistant", "content": bot_reply})

        # Save updated history
        save_history(chat_history)

        return bot_reply, chat_history
    except Exception as e:
        return f"⚠️ Error: {e}", chat_history

def chatbot():
    print("🤖 Welcome to Conversational AI Chatbot (Gemini-Powered, Persistent Memory!)")

    # Load previous history or start fresh
    chat_history = load_history()

    while True:
        print("\nChoose a function:")
        print("1. Casual Chat")
        print("2. Information Provider")
        print("3. Recommendations")
        print("4. Clear Memory")
        print("5. Exit")

        choice = input("Enter choice: ")

        if choice == "5":
            print("Goodbye 👋 (your chat history has been saved!)")
            save_history(chat_history)
            break

        if choice == "4":
            print("🧹 Memory cleared!")
            chat_history = [{"role": "system", "content": "You are a helpful and friendly AI chatbot."}]
            save_history(chat_history)
            continue

        user_input = input("You: ")
        response, chat_history = get_response(user_input, choice, chat_history)
        print("Chatbot:", response)

        # Feedback logging
        feedback = input("Was this helpful? (yes/no): ")
        with open("feedback.txt", "a", encoding="utf-8") as f:
            f.write(f"User: {user_input} | Response: {response} | Feedback: {feedback}\n")

if __name__ == "__main__":
    chatbot()
