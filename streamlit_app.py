import os
import random
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# Import prompt templates
from prompts import casual_chat_prompts, info_prompts, recommendation_prompts

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

FEEDBACK_FILE = "feedback.txt"

# ---------------- Helpers ----------------
def log_feedback(user_input, bot_reply, rating, function, prompt_used):
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(f"User: {user_input} | Response: {bot_reply} | Function: {function} | Prompt: {prompt_used} | Feedback: {rating}\n")

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="😎 AI Assistant 😎", page_icon="🤖", layout="centered")
st.title("🤖 M Tarini's AI Assistant")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Initialize per-user session history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function selector
function_choice = st.radio(
    "Select a Function:",
    ["Casual Chat", "Information Provider", "Recommendations"]
)

# Show chat history
for msg in st.session_state.messages:
    role_icon = "🤖" if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"]):
        st.markdown(f"{role_icon} {msg['content']}")

# ---------------- User Input ----------------
if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f"🧑 {user_input}")

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("🤖 ...typing")

        try:
            # Pick prompt template based on function
            if function_choice == "Casual Chat":
                prompt_template = random.choice(casual_chat_prompts)
            elif function_choice == "Information Provider":
                prompt_template = random.choice(info_prompts)
            else:  # Recommendations
                prompt_template = random.choice(recommendation_prompts)

            # Build conversation history for memory
            conversation = []
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                conversation.append({"role": role, "parts": [msg["content"]]})

            # Add the latest user input formatted with template
            prompt = prompt_template.format(user_input=user_input)
            conversation.append({"role": "user", "parts": [prompt]})

            # Generate with Gemini (with context)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(conversation)
            bot_reply = response.text.strip()

            # Show reply
            placeholder.markdown(f"🤖 {bot_reply}")

            # Save chat in session only
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

            # Feedback buttons
            col1, col2 = st.columns(2)
            if col1.button("👍 Helpful", key=f"up_{len(st.session_state.messages)}"):
                log_feedback(user_input, bot_reply, "positive", function_choice, prompt_template)
                st.success("Feedback saved!")
            if col2.button("👎 Not Helpful", key=f"down_{len(st.session_state.messages)}"):
                log_feedback(user_input, bot_reply, "negative", function_choice, prompt_template)
                st.warning("Feedback saved!")

        except Exception as e:
            placeholder.markdown(f"⚠️ Error: {e}")
