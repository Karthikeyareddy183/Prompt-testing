# Filename: app.py

import streamlit as st
import requests
import os
from dotenv import load_dotenv
load_dotenv()


# ================================
# CONFIGURATION
# ================================
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")  # Store securely!
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL_NAME = "open-mistral-7b"

HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

# ================================
# STREAMLIT UI
# ================================
st.set_page_config(page_title="Mistral Chatbot", page_icon="🤖")
st.title("🧠 Mistral Conversational Chatbot")
st.markdown(
    "This chatbot remembers your conversation. "
    "You can edit the **system prompt** below to change its behavior."
)

# ================================
# SYSTEM PROMPT
# ================================
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful assistant."

st.session_state.system_prompt = st.text_area(
    "📝 System Prompt",
    value=st.session_state.system_prompt,
    height=100
)

# ================================
# CHAT MEMORY
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": st.session_state.system_prompt}
    ]

# ================================
# RESET CHAT BUTTON
# ================================
if st.button("🔄 Reset Chat"):
    st.session_state.messages = [
        {"role": "system", "content": st.session_state.system_prompt}
    ]
    st.success("Chat memory reset!")

# ================================
# DISPLAY PAST MESSAGES
# ================================
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ================================
# USER INPUT
# ================================
if prompt := st.chat_input("Say something..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Regenerate system prompt if changed
    st.session_state.messages[0]["content"] = st.session_state.system_prompt

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Mistral API
    payload = {
        "model": MODEL_NAME,
        "messages": st.session_state.messages
    }

    response = requests.post(MISTRAL_API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        assistant_message = response.json()["choices"][0]["message"]["content"]

        # Add assistant message to memory
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_message})

        # Display assistant message
        with st.chat_message("assistant"):
            st.markdown(assistant_message)
    else:
        st.error(f"API Error: {response.status_code} - {response.text}")
