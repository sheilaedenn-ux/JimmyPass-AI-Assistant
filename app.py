import streamlit as st
import json
import os
import requests

# --- Get API key from Streamlit Secrets ---
HF_API_KEY = os.getenv("HF_API_KEY")

# --- Load FAQs ---
with open("faq.json", "r", encoding="utf-8") as f:
    faq_data = json.load(f)

# --- Streamlit Setup ---
st.set_page_config(page_title="JimmyPass AI Assistant", layout="centered")
st.title("🎓 JimmyPass AI Assistant")
st.write("Hello! I’m your virtual assistant. Ask me anything about JimmyPass Educational & Consulting Enugu.")

# --- Lead Capture ---
if "lead_collected" not in st.session_state:
    st.session_state.lead_collected = False

if not st.session_state.lead_collected:
    with st.form("lead_form"):
        st.subheader("Quick Info for Personalized Assistance")
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        phone = st.text_input("Your Phone (optional)")
        submitted = st.form_submit_button("Start Chat")

        if submitted:
            if name and email:
                st.session_state.lead_collected = True
                st.session_state.user_info = {
                    "name": name,
                    "email": email,
                    "phone": phone
                }
                st.success(f"Thanks {name}! You can now ask your questions below.")
            else:
                st.warning("Please provide at least your name and email.")

# --- Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- Hugging Face API Call ---
def query_huggingface(prompt):
    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct:cerebras",
        "messages": [
            {
                "role": "system",
                "content": "You are JimmyPass AI Assistant, a professional educational consultant in Enugu."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        return "Sorry, the AI service is currently unavailable. Please try again later."

    data = response.json()
    return data["choices"][0]["message"]["content"]

# --- User Input ---
if st.session_state.lead_collected:
    user_input = st.chat_input("Ask me about JimmyPass services...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        faq_text = "\n".join([f"{k}: {v}" for k, v in faq_data.items()])
        prompt = (
            f"Use the following info to answer client questions:\n{faq_text}\n\n"
            f"Client asked: {user_input}\n"
            f"Respond clearly, politely, and professionally. "
            f"If unsure, suggest contacting JimmyPass on Facebook."
        )

        response = query_huggingface(prompt)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        with st.chat_message("assistant"):
            st.write(response)
