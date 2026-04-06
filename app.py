import streamlit as st
from groq import Groq
import random
import time
import os

# 🔑 API KEY (SAFE)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(layout="wide", page_title="Sitcom Chat", page_icon="💬")

# -------------------------------
# 🎨 UI STYLE
# -------------------------------
st.markdown("""
<style>
.stApp { background-color: #111b21; }

.header {
    background-color: #202c33;
    padding: 12px;
    color: white;
    text-align: center;
    font-weight: bold;
    border-bottom: 1px solid #333;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# MODE SWITCH
# -------------------------------
mode = st.sidebar.radio("Mode", ["1-to-1 Chat", "Group Chat"])

# -------------------------------
# CHARACTERS
# -------------------------------
characters = [
    "Chandler Bing",
    "Michael Scott",
    "Sheldon Cooper",
    "Joey Tribbiani",
    "Ross Geller",
    "Dwight Schrute",
    "Jim Halpert",
    "Howard Wolowitz"
]

# -------------------------------
# AVATARS (FIXED → images/)
# -------------------------------
avatars = {
    "Chandler Bing": "images/chandler.jpg",
    "Michael Scott": "images/michael.jpg",
    "Sheldon Cooper": "images/sheldon.jpg",
    "Joey Tribbiani": "images/joey.jpg",
    "Ross Geller": "images/ross.jpg",
    "Dwight Schrute": "images/dwight.jpg",
    "Jim Halpert": "images/jim.jpg",
    "Howard Wolowitz": "images/howard.jpg"
}

def safe_avatar(character):
    path = avatars.get(character)
    if path and os.path.exists(path):
        return path
    return "https://i.imgur.com/8RKXAIV.png"

# -------------------------------
# CLEAN MESSAGES
# -------------------------------
def clean_messages(msgs):
    return [{"role": m["role"], "content": m["content"]} for m in msgs]

# -------------------------------
# MESSAGE TICKS
# -------------------------------
def get_ticks(status):
    if status == "sent":
        return "✔"
    elif status == "delivered":
        return "✔✔"
    elif status == "seen":
        return "✔✔ 🔵"
    return ""

# -------------------------------
# SIGNATURE LINES
# -------------------------------
signature_lines = {
    "Michael Scott": ["That's what she said!"],
    "Chandler Bing": ["Could I BE any more obvious?"],
    "Sheldon Cooper": ["Bazinga!"],
    "Joey Tribbiani": ["How you doin?"],
    "Ross Geller": ["We were on a break!"],
    "Dwight Schrute": ["False."],
    "Jim Halpert": ["Classic."],
    "Howard Wolowitz": ["I'm irresistible."]
}

# -------------------------------
# PROMPT
# -------------------------------
def get_prompt(character):
    return f"""
You are {character}.
Stay in character.
User is a different person.
Reply in 1 short funny line.
"""

# -------------------------------
# MODEL (WITH FALLBACK)
# -------------------------------
def generate_reply(character, msgs, max_tokens=60):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": get_prompt(character)},
                *clean_messages(msgs)
            ],
            max_tokens=max_tokens,
            temperature=0.9
        )
    except:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": get_prompt(character)},
                *clean_messages(msgs)
            ],
            max_tokens=max_tokens,
            temperature=0.9
        )

    return response.choices[0].message.content.strip().split("\n")[0]

# =====================================================
# 🧑 1-to-1 CHAT
# =====================================================
if mode == "1-to-1 Chat":

    character = st.sidebar.selectbox("Select Character", characters)

    st.markdown(f"<div class='header'>🟢 {character} (Online)</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>last seen just now</p>", unsafe_allow_html=True)

    if "private_chats" not in st.session_state:
        st.session_state.private_chats = {}

    if character not in st.session_state.private_chats:
        st.session_state.private_chats[character] = []

    messages = st.session_state.private_chats[character]

    for msg in messages:
        with st.chat_message(msg["role"], avatar=safe_avatar(character)):
            if msg["role"] == "user":
                ticks = get_ticks(msg.get("status", ""))
                st.markdown(f"{msg['content']} <span style='color:gray;'>{ticks}</span>", unsafe_allow_html=True)
            else:
                st.write(msg["content"])

    user_input = st.chat_input("Message...")

    if user_input:
        messages.append({"role": "user", "content": user_input, "status": "sent"})

        with st.chat_message("user"):
            st.write(user_input)

        messages[-1]["status"] = "delivered"
        time.sleep(0.3)
        messages[-1]["status"] = "seen"

        with st.chat_message("assistant", avatar=safe_avatar(character)):
            typing = st.empty()
            typing.markdown(f"<span style='color:lightgreen;'>🟢 {character} is typing...</span>", unsafe_allow_html=True)
            time.sleep(random.uniform(0.8, 1.5))

        reply = generate_reply(character, messages[-6:])

        if random.random() < 0.3:
            reply += " " + random.choice(signature_lines[character])

        messages.append({"role": "assistant", "content": reply})
        typing.markdown(reply)

# =====================================================
# 👥 GROUP CHAT
# =====================================================
else:

    st.markdown("<div class='header'>💬 Sitcom Group Chat (Online 🟢)</div>", unsafe_allow_html=True)

    if "group_chat" not in st.session_state:
        st.session_state.group_chat = []

    messages = st.session_state.group_chat

    for msg in messages:
        avatar = safe_avatar(msg.get("name"))

        with st.chat_message(msg["role"], avatar=avatar):
            if msg["role"] == "assistant":
                st.markdown(f"**{msg['name']}**: {msg['content']}")
            else:
                ticks = get_ticks(msg.get("status", ""))
                st.markdown(f"{msg['content']} <span style='color:gray;'>{ticks}</span>", unsafe_allow_html=True)

    user_input = st.chat_input("Message group...")

    if user_input:
        messages.append({"role": "user", "content": user_input, "status": "sent"})

        with st.chat_message("user"):
            st.write(user_input)

        messages[-1]["status"] = "delivered"
        time.sleep(0.3)
        messages[-1]["status"] = "seen"

        active_characters = random.sample(characters, k=random.randint(2, 3))

        for character in active_characters:

            with st.chat_message("assistant", avatar=safe_avatar(character)):
                typing = st.empty()
                typing.markdown(f"<span style='color:lightgreen;'>🟢 {character} is typing...</span>", unsafe_allow_html=True)
                time.sleep(random.uniform(0.8, 1.5))

            reply = generate_reply(character, messages[-5:], max_tokens=40)

            if random.random() < 0.3:
                reply += " " + random.choice(signature_lines[character])

            messages.append({
                "role": "assistant",
                "name": character,
                "content": reply
            })

            typing.markdown(f"**{character}**: {reply}")