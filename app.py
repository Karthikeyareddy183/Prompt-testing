import streamlit as st
import requests
import os  # Keep os for potential future use, though not directly used for secrets here

# ================================
# CONFIGURATION
# ================================
# Use st.secrets for securely accessing API keys in Streamlit Cloud
# For local development, create a .streamlit/secrets.toml file:
# [MISTRAL_API_KEY]
# MISTRAL_API_KEY = "your_mistral_api_key_here"
MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]
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

# Use a key to prevent re-rendering issues if the text area is modified
st.session_state.system_prompt = st.text_area(
    "📝 System Prompt",
    value=st.session_state.system_prompt,
    height=100,
    key="system_prompt_input"  # Added a key for stability
)

# ================================
# CHAT MEMORY
# ================================
# Initialize messages with the system prompt if not already present
# This ensures the system prompt is always the first message
if "messages" not in st.session_state or st.session_state.messages[0]["role"] != "system" or st.session_state.messages[0]["content"] != st.session_state.system_prompt:
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
    # Rerun the app to clear displayed messages immediately after reset
    st.experimental_rerun()

# ================================
# DISPLAY PAST MESSAGES
# ================================
# Start displaying from the second message, as the first is the system prompt
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ================================
# USER INPUT AND API CALL
# ================================
if prompt := st.chat_input("Say something..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare messages for the API call, ensuring the system prompt is current
    messages_for_api = [
        {"role": "system", "content": st.session_state.system_prompt}
    ] + [msg for msg in st.session_state.messages if msg["role"] != "system"]  # Exclude system message if already in messages

    payload = {
        "model": MODEL_NAME,
        "messages": messages_for_api
    }

    with st.spinner("Thinking..."):  # Add a spinner while waiting for response
        try:
            response = requests.post(
                MISTRAL_API_URL, headers=HEADERS, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            assistant_message = response.json(
            )["choices"][0]["message"]["content"]

            # Add assistant message to memory
            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_message})

            # Display assistant message
            with st.chat_message("assistant"):
                st.markdown(assistant_message)
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")
            st.error(
                f"Response content: {response.text if 'response' in locals() else 'No response received'}")
        except KeyError:
            st.error("Error parsing API response. Unexpected format.")
            st.error(
                f"Full response: {response.json() if 'response' in locals() else 'No JSON response'}")
