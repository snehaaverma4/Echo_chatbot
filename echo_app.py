import streamlit as st
from groq import Groq
import csv
import os
from datetime import datetime

# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Echo",
    page_icon="🔮",
    layout="centered"
)

# ─── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e8e6f0;
}

/* Hide Streamlit defaults */
#MainMenu, footer, header {visibility: hidden;}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 780px;
}

/* Header */
.echo-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem 0;
}
.echo-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1;
}
.echo-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 300;
    color: #6b6880;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.4rem;
}

/* Divider */
.echo-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #2d2b3d, transparent);
    margin: 1.5rem 0;
}

/* Chat messages */
.user-bubble {
    display: flex;
    justify-content: flex-end;
    margin: 0.8rem 0;
}
.user-bubble-inner {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: #ffffff;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 75%;
    font-size: 0.92rem;
    line-height: 1.5;
    box-shadow: 0 4px 20px rgba(79, 70, 229, 0.3);
}
.bot-bubble {
    display: flex;
    justify-content: flex-start;
    margin: 0.8rem 0;
    align-items: flex-end;
    gap: 0.6rem;
}
.bot-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    flex-shrink: 0;
    box-shadow: 0 0 12px rgba(167, 139, 250, 0.4);
}
.bot-bubble-inner {
    background: #16141f;
    border: 1px solid #2d2b3d;
    color: #e8e6f0;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    max-width: 75%;
    font-size: 0.92rem;
    line-height: 1.6;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

/* Feedback row */
.feedback-row {
    display: flex;
    gap: 0.4rem;
    margin-left: 2.4rem;
    margin-top: -0.3rem;
    margin-bottom: 0.5rem;
}

/* Stats bar */
.stats-bar {
    background: #16141f;
    border: 1px solid #2d2b3d;
    border-radius: 12px;
    padding: 0.75rem 1.2rem;
    display: flex;
    gap: 2rem;
    margin-bottom: 1rem;
    font-size: 0.8rem;
    color: #6b6880;
}
.stat-item span {
    color: #a78bfa;
    font-weight: 600;
    font-family: 'Syne', sans-serif;
}

/* Input area */
.stChatInput {
    border-radius: 16px !important;
}
stChatInput > div {
    background: #16141f !important;
    border: 1px solid #2d2b3d !important;
}

/* Buttons */
.stButton > button {
    background: #1e1c2e !important;
    border: 1px solid #2d2b3d !important;
    color: #9ca3af !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    padding: 0.2rem 0.7rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    border-color: #a78bfa !important;
    color: #a78bfa !important;
    background: #1e1c2e !important;
}

/* Clear button */
.clear-btn > button {
    background: transparent !important;
    border: 1px solid #2d2b3d !important;
    color: #4a4860 !important;
    font-size: 0.75rem !important;
}

/* Scrollable chat area */
.chat-container {
    max-height: 520px;
    overflow-y: auto;
    padding: 0.5rem 0;
    scrollbar-width: thin;
    scrollbar-color: #2d2b3d transparent;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 3rem 0;
    color: #3d3b52;
}
.empty-icon {
    font-size: 2.5rem;
    margin-bottom: 0.8rem;
}
.empty-text {
    font-size: 0.9rem;
    font-weight: 300;
}

/* Suggestion chips */
.chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
    margin-top: 1rem;
}
.chip {
    background: #16141f;
    border: 1px solid #2d2b3d;
    border-radius: 20px;
    padding: 0.35rem 0.9rem;
    font-size: 0.78rem;
    color: #6b6880;
    cursor: pointer;
    transition: all 0.2s;
}
</style>
""", unsafe_allow_html=True)

# ─── Init session state ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = set()
if "thumbs_up" not in st.session_state:
    st.session_state.thumbs_up = 0
if "thumbs_down" not in st.session_state:
    st.session_state.thumbs_down = 0

# ─── Groq Client ───────────────────────────────────────────────
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are Echo, a sharp and thoughtful AI assistant. "
        "You give clear, concise, and helpful responses. "
        "You don't pad answers unnecessarily. "
        "When you don't know something, say so honestly."
    )
}

# ─── Feedback logger ───────────────────────────────────────────
def save_feedback(prompt, response, rating):
    file_exists = os.path.isfile("feedback_log.csv")
    with open("feedback_log.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "prompt", "response", "rating"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            prompt, response, rating
        ])

# ─── Header ────────────────────────────────────────────────────
st.markdown("""
<div class="echo-header">
    <p class="echo-title">Echo</p>
    <p class="echo-sub">AI Assistant · Powered by LLaMA 3</p>
</div>
<div class="echo-divider"></div>
""", unsafe_allow_html=True)

# ─── Stats bar ─────────────────────────────────────────────────
total = len([m for m in st.session_state.messages if m["role"] == "user"])
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.markdown(f"""<div style="text-align:center; font-size:0.8rem; color:#6b6880;">
        Messages <span style="color:#a78bfa; font-weight:600; font-family:Syne;">{total}</span>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div style="text-align:center; font-size:0.8rem; color:#6b6880;">
        👍 <span style="color:#34d399; font-weight:600; font-family:Syne;">{st.session_state.thumbs_up}</span>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div style="text-align:center; font-size:0.8rem; color:#6b6880;">
        👎 <span style="color:#f87171; font-weight:600; font-family:Syne;">{st.session_state.thumbs_down}</span>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

# ─── Chat Display ──────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🔮</div>
        <div class="empty-text">Echo is listening. Say something.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="user-bubble">
                <div class="user-bubble-inner">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

        elif msg["role"] == "assistant":
            st.markdown(f"""
            <div class="bot-bubble">
                <div class="bot-avatar">✦</div>
                <div class="bot-bubble-inner">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

            # Feedback buttons for each assistant message
            if i not in st.session_state.feedback_given:
                prev_user = ""
                for j in range(i - 1, -1, -1):
                    if st.session_state.messages[j]["role"] == "user":
                        prev_user = st.session_state.messages[j]["content"]
                        break

                fb_col1, fb_col2, fb_col3 = st.columns([0.08, 0.08, 0.84])
                with fb_col1:
                    if st.button("👍", key=f"up_{i}"):
                        save_feedback(prev_user, msg["content"], "positive")
                        st.session_state.feedback_given.add(i)
                        st.session_state.thumbs_up += 1
                        st.rerun()
                with fb_col2:
                    if st.button("👎", key=f"dn_{i}"):
                        save_feedback(prev_user, msg["content"], "negative")
                        st.session_state.feedback_given.add(i)
                        st.session_state.thumbs_down += 1
                        st.rerun()
            else:
                st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

# ─── Clear Chat ────────────────────────────────────────────────
if st.session_state.messages:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("✕ Clear chat", key="clear"):
        st.session_state.messages = []
        st.session_state.feedback_given = set()
        st.rerun()

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ─── Chat Input ────────────────────────────────────────────────
user_input = st.chat_input("Ask Echo anything...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.spinner(""):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[SYSTEM_PROMPT] + st.session_state.messages,
            max_tokens=1024,
            temperature=0.7
        )

    bot_reply = response.choices[0].message.content
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })
    st.rerun()
