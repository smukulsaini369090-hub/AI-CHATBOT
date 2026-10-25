import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# 3. Smart Auto-Model Selector (Prioritizing gemini-3.5-flash)
@st.cache_resource
def load_best_model():
    preferred_models = [
        "gemini-3.5-flash",
        "gemini-3.8-flash",
        "gemini-2.5-flash",
        "gemini-pro"
    ]
    try:
        available = [
            m.name.replace("models/", "")
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        for pm in preferred_models:
            if pm in available:
                return genai.GenerativeModel(pm), pm
        if available:
            return genai.GenerativeModel(available[0]), available[0]
    except Exception:
        pass
    return genai.GenerativeModel("gemini-3.5-flash"), "gemini-3.5-flash"

# 4. Streamlit Page Configuration
st.set_page_config(page_title="Chatbot by MUKUL", page_icon="🤖")
st.title("🤖 Chatbot by MUKUL")

model, active_model_name = load_best_model()
st.caption(f"⚡ Powered by: `{active_model_name}`")

# 5. Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. Display previous chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Chat Input & Response Generation
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = model.generate_content(prompt)
                reply = response.text
                st.markdown(reply)
            except Exception as e:
                st.error(f"Error: {e}")
                reply = "Sorry, I encountered an error."

    st.session_state.messages.append({"role": "assistant", "content": reply})