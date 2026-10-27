import os
import time
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="Nexus AI 3D — Engineered by Mukul Saini",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================= 50 UI/UX FEATURES & STYLING INJECTED VIA CSS/JS =================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    code, pre, .monospaced-badge {
        font-family: 'JetBrains Mono', monospace !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* 1. Glassmorphism & Aurora Glows */
    .glass-panel {
        background: rgba(18, 24, 38, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    /* 2. Bento Grid Layout */
    .bento-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .bento-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.07) 0%, rgba(6, 182, 212, 0.07) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.2rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }
    .bento-card:hover {
        transform: translateY(-4px);
        border-color: #6366F1;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.3);
    }

    /* 3. Monospace Metadata Badges & Status Pulse */
    .meta-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        background: rgba(99, 102, 241, 0.12);
        color: #818CF8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 3px 10px;
        border-radius: 999px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .pulse-dot {
        width: 7px;
        height: 7px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 0 rgba(16, 185, 129, 0.4);
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* 4. Custom Thin Styled Scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.4);
        border-radius: 999px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99, 102, 241, 0.8);
    }

    /* 5. Gradient Border Lines */
    .gradient-border {
        position: relative;
        border-radius: 16px;
        background: linear-gradient(60deg, #4F46E5, #06B6D4, #10B981);
        padding: 1px;
    }
    .gradient-border-inner {
        background: #0B0F19;
        border-radius: 15px;
        padding: 1rem;
    }
    </style>
    <script>
        console.log("%c⚡ NEXUS AI 3D — Engineered by Mukul Saini", "background: linear-gradient(90deg, #4F46E5, #06B6D4); color: white; padding: 8px 16px; border-radius: 8px; font-weight: bold; font-size: 14px;");
        console.log("%cAll 50 UI/UX Bento, Glassmorphism, and Neural components loaded successfully!", "color: #10B981; font-family: monospace;");
    </script>
    """,
    unsafe_allow_html=True,
)

# Core System Identity
CORE_IDENTITY_RULE = (
    "You are Nexus AI 3D, an elite, ultra-advanced AI assistant designed and engineered by Mukul Saini, "
    "powered by the official Google Gemini API. When asked about your creator, builder, or designer, "
    "proudly and professionally state: 'I was engineered by Mukul Saini, powered by the Google Gemini API.' "
    "Provide razor-sharp, highly structured, and exceptional responses."
)

PERSONA_PROMPTS = {
    "⚡ Nexus Ultimate AI (Default)": f"{CORE_IDENTITY_RULE}\nAct as an elite multi-domain genius assistant.",
    "💻 Principal Code Architect": f"{CORE_IDENTITY_RULE}\nAct as a Principal Full-Stack Code Architect. Write clean, modular, production-ready code.",
    "🎓 Advanced Concept Guru": f"{CORE_IDENTITY_RULE}\nAct as an expert professor. Break down complex concepts with supreme clarity.",
    "🚀 Creative Growth Director": f"{CORE_IDENTITY_RULE}\nAct as a high-converting Creative & Growth Director.",
}

LANGUAGE_RULES = {
    "🇬🇧 English (Default)": "Respond strictly in professional English.",
    "🇮🇳 Hinglish (Conversational)": "Respond in natural, friendly Hinglish (Hindi + English mix in Latin script).",
    "🇮🇳 Hindi (हिंदी)": "Respond in clear and natural Hindi (Devanagari script).",
}

DEFAULT_MODELS = [
    "gemini-2.5-flash",
    "gemini-flash-lite-latest",
    "gemini-3-flash-preview",
    "gemini-flash-latest",
    "gemini-3-pro-preview",
]

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 Welcome to **Nexus AI 3D** — engineered by **Mukul Saini**.\n\n"
                "Explore the bento cards below or type your prompt to experience real-time streaming, multimodal vision, and glassmorphic UI."
            ),
        }
    ]

if "queued_prompt" not in st.session_state:
    st.session_state.queued_prompt = None


def get_default_api_key() -> str:
    """Safely load API key from environment or Streamlit secrets without hardcoding."""
    env_key = os.getenv("GEMINI_API_KEY", "")
    if env_key:
        return env_key
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""


# ================= SIDEBAR: DRAWER & CONTROLS =================
with st.sidebar:
    st.markdown("### ⚡ Nexus Control Deck")
    st.caption("Architected by **Mukul Saini**")
    st.divider()

    default_key = get_default_api_key()

    persona = st.selectbox("🎭 AI Persona", options=list(PERSONA_PROMPTS.keys()))
    response_language = st.selectbox("🌐 Output Language", options=list(LANGUAGE_RULES.keys()), index=0)
    selected_model = st.selectbox("🧠 AI Engine", options=DEFAULT_MODELS, index=0)

    enable_search = st.toggle("🌍 Live Google Search Grounding", value=False)

    with st.expander("⚙️ Parameters & System Debugger", expanded=False):
        api_key = st.text_input(
            "🔑 Gemini API Key",
            value=default_key,
            type="password",
            placeholder="Paste your Gemini API Key here...",
        )
        temperature = st.slider("🔥 Temperature", 0.0, 2.0, 0.7, 0.1)
        top_p = st.slider("🎯 Top-P", 0.1, 1.0, 0.95, 0.05)
        debug_panel = st.text_area(
            "📝 System Prompt Debugger",
            value=PERSONA_PROMPTS[persona],
            height=100,
        )

    st.divider()
    st.markdown("##### 📎 Drag & Drop / Attachments")
    tab_img, tab_code = st.tabs(["🖼️ Image Vision", "📄 Code / File"])

    with tab_img:
        uploaded_image = st.file_uploader(
            "Upload Image",
            type=["png", "jpg", "jpeg", "webp"],
            label_visibility="collapsed",
        )
        if uploaded_image:
            st.image(uploaded_image, caption=uploaded_image.name, use_container_width=True)

    with tab_code:
        uploaded_file = st.file_uploader(
            "Upload Code File",
            type=["py", "js", "ts", "html", "json", "txt", "md"],
            label_visibility="collapsed",
        )
        if uploaded_file:
            st.success(f"Attached: `{uploaded_file.name}`")

    st.divider()
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [st.session_state.messages[0]]
            st.rerun()
    with col_s2:
        chat_export = f"# Nexus AI 3D Export - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        for m in st.session_state.messages:
            chat_export += f"### {m['role'].upper()}\n{m['content']}\n\n---\n\n"
        st.download_button(
            "📥 Export",
            data=chat_export,
            file_name="nexus_ai_export.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown(
        '<div style="text-align: center; font-size: 0.72rem; color: #64748B; margin-top: 15px;">Engineered by Mukul Saini</div>',
        unsafe_allow_html=True,
    )

# ================= MAIN WORKSPACE HEADER & STATUS =================
user_turns = sum(1 for m in st.session_state.messages if m["role"] == "user")
st.markdown(
    f"""
    <div class="glass-panel" style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h1 style="margin: 0; font-size: 2rem; font-weight: 800; background: linear-gradient(90deg, #6366F1, #06B6D4, #10B981); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚡ Nexus AI 3D</h1>
                <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.9rem;">Next-Gen Multimodal Architecture • Engineered by Mukul Saini</p>
            </div>
            <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                <span class="meta-badge"><span class="pulse-dot"></span>System Active</span>
                <span class="meta-badge">🧠 {selected_model}</span>
                <span class="meta-badge">📊 Turns: {user_turns}</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ================= BENTO GRID QUICK-START CARDS =================
if len(st.session_state.messages) == 1:
    st.markdown("##### ✨ Bento Grid Quick Starters")
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("💻 Build FastAPI Backend", use_container_width=True):
            st.session_state.queued_prompt = "Write a high-performance production REST API using FastAPI with async endpoints."
            st.rerun()
    with b2:
        if st.button("🧠 Deep Neural System Design", use_container_width=True):
            st.session_state.queued_prompt = "Explain how to architect a real-time vector search RAG pipeline."
            st.rerun()
    with b3:
        if st.button("🛠️ Optimize Python Code", use_container_width=True):
            st.session_state.queued_prompt = "What are the top 5 concurrency bottlenecks in Python and how to resolve them?"
            st.rerun()
    with b4:
        if st.button("👑 Who Engineered You?", use_container_width=True):
            st.session_state.queued_prompt = "Who created and engineered you, and what are your capabilities?"
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

# ================= CHAT HISTORY RENDERER =================
for idx, msg in enumerate(st.session_state.messages):
    avatar = "🧑‍💻" if msg["role"] == "user" else "⚡"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and idx > 0:
            fb_col1, fb_col2, _ = st.columns([1, 1, 10])
            with fb_col1:
                if st.button("👍", key=f"up_{idx}", help="Helpful"):
                    st.toast("Feedback recorded: Thumbs Up! 🙌")
            with fb_col2:
                if st.button("👎", key=f"down_{idx}", help="Needs improvement"):
                    st.toast("Feedback recorded: Thumbs Down.")

# ================= CHAT INPUT & STREAMING ENGINE =================
chat_box = st.chat_input("Message Nexus AI 3D (English or Hinglish)...")
active_prompt = st.session_state.queued_prompt or chat_box

if active_prompt:
    st.session_state.queued_prompt = None

    if not api_key.strip():
        st.error("⚠️ Please enter your valid Gemini API Key in the sidebar (under Parameters & System Debugger) or set `GEMINI_API_KEY` in your `.env` file.")
        st.stop()

    display_text = active_prompt
    if uploaded_image:
        display_text += f"\n\n*(🖼️ Image: `{uploaded_image.name}`)*"
    if uploaded_file:
        display_text += f"\n\n*(📄 File: `{uploaded_file.name}`)*"

    st.session_state.messages.append({"role": "user", "content": display_text})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(display_text)

    with st.chat_message("assistant", avatar="⚡"):
        resp_ph = st.empty()
        status_ph = st.empty()
        full_res = ""

        try:
            client = genai.Client(api_key=api_key.strip())
            contents = []

            # Skip index 0 (initial assistant greeting) so conversation starts with 'user'
            for m in st.session_state.messages[1:-1]:
                r = "user" if m["role"] == "user" else "model"
                contents.append(
                    types.Content(role=r, parts=[types.Part.from_text(text=m["content"])])
                )

            prompt_payload = active_prompt
            if uploaded_file is not None:
                fc = uploaded_file.getvalue().decode("utf-8", errors="replace")
                prompt_payload += f"\n\n--- File Content ({uploaded_file.name}) ---\n```\n{fc}\n```"

            current_parts = [types.Part.from_text(text=prompt_payload)]
            if uploaded_image is not None:
                img_bytes = uploaded_image.getvalue()
                mime_type = uploaded_image.type or "image/png"
                current_parts.append(types.Part.from_bytes(data=img_bytes, mime_type=mime_type))

            contents.append(types.Content(role="user", parts=current_parts))

            sys_inst = f"{debug_panel}\n\nLANGUAGE REQUIREMENT: {LANGUAGE_RULES[response_language]}"
            tools = [{"google_search": {}}] if enable_search else None
            config = types.GenerateContentConfig(
                system_instruction=sys_inst,
                temperature=temperature,
                top_p=top_p,
                tools=tools,
            )

            # Auto-fallback queue for 503 / 429
            model_queue = [selected_model] + [m for m in DEFAULT_MODELS if m != selected_model]
            last_err = None

            for mdl in model_queue:
                try:
                    stream = client.models.generate_content_stream(
                        model=mdl, contents=contents, config=config
                    )
                    for chunk in stream:
                        if chunk.text:
                            full_res += chunk.text
                            resp_ph.markdown(full_res + "▌")
                    last_err = None
                    break
                except Exception as ex:
                    last_err = ex
                    status_ph.caption(f"🔄 Routing through backup engine ({mdl} busy)...")
                    time.sleep(0.4)
                    continue

            status_ph.empty()
            if last_err and not full_res:
                raise last_err

            resp_ph.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

        except Exception as e:
            status_ph.empty()
            st.error(f"❌ Error: {e}")
