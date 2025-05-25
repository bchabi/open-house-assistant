import streamlit as st
from gtts import gTTS
from io import BytesIO
from PIL import Image
import base64
from openai import OpenAI

# ---------- Config ----------
st.set_page_config(page_title="Open House Assistant", page_icon="🏫", layout="wide")

# ---------- Initialize OpenAI Client ----------

client = OpenAI(api_key=st.secrets["openai_api_key"])
# ---------- Static Q&A ----------
qa_pairs = {
    "Who is the principal": "Ms. Anne Yam",
    "Who is the vice principal": "Ms. Eleni Gardikiotis",
    "What subjects do you learn": "Math, science, Mandarin, French, coding, English Languge arts, Social studies, Physical education, Social emotional learning, Music, Art, Religion, Career/Health education",
    "What are the school hours": "8:30 to 3:30 every day, except Wednesday: 8:30 to 2:30",
    "What sport events do you have": "Track and field, soccer, basketball, volleyball, cross country",
    "What extra-curricular activities are there?": "Destination Imagination, Intermediate and primary choir, Afterschool sports, Green club, Leadership club, Peer helpers club, Running club, Art club, G-square, Alter servers, Math enrichment",
    "What is the tuition fee": "Maximum $580/month"
}

# ---------- Session State ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "image_audio_bytes" not in st.session_state:
    st.session_state.image_audio_bytes = None

# ---------- TTS ----------
def speak(text):
    tts = gTTS(text)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    return mp3_fp.getvalue()

# ---------- GPT Vision Description ----------
def describe_image(image_data, prompt):
    base64_image = base64.b64encode(image_data).decode("utf-8")
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high"
                    }
                ]
            }
        ]
    )
    return response.output_text.strip()

# ---------- Header ----------
st.markdown("""
    <h1 style='text-align: center; color:#004466;'>🏫 Open House Assistant</h1>
    <p style='text-align: center; font-size:18px;'>Making school tours inclusive and informative for everyone.</p>
    <hr style='border-top: 2px solid #004466;'/>
""", unsafe_allow_html=True)

# ---------- Layout ----------
col1, col2 = st.columns([3, 1.3], gap="large")

# ---------- Left Column: Predefined Questions ----------
with col1:
    st.markdown("### 📝 Ask a Question")

    with st.container(border=True):
        st.markdown("#### 💬 Chat History")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if st.session_state.audio_bytes:
            st.audio(st.session_state.audio_bytes, format="audio/mp3")

    # Predefined buttons
    for question in qa_pairs.keys():
        if st.button(f"❓ {question}", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": question})
            answer = qa_pairs[question]
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.session_state.audio_bytes = speak(answer)
            st.rerun()

    # Reset button
    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.audio_bytes = None
        st.session_state.image_audio_bytes = None
        st.rerun()

# ---------- Right Column: Camera Vision ----------
with col2:
    st.markdown("### 📷 Visual Help Station")
    mode = st.selectbox("Choose Mode:", ["🧠 Analyze Room", "🤟 Interpret ASL"])

    picture = st.camera_input("Capture Image")

    if picture:
        st.image(picture, caption="📸 Image captured", use_container_width=True)

        with st.spinner("Processing image..."):
            try:
                image_data = picture.getvalue()

                if mode == "🧠 Analyze Room":
                    prompt = "Describe this image in detail to a visually impaired person."
                else:
                    prompt = "What ASL letter is the person showing in this image? Only describe the letter being signed."

                description = describe_image(image_data, prompt)

                st.markdown("**🧠 Description:**")
                st.markdown(description)

                st.session_state.image_audio_bytes = speak(description)
                st.audio(st.session_state.image_audio_bytes, format="audio/mp3")

            except Exception as e:
                st.error(f"❌ Error generating description: {e}")

# ---------- Footer ----------
st.markdown("""
    <hr>
    <p style='text-align: center; font-size: 14px; color: gray;'>
        Built with ❤️ to support accessibility at school open houses.
    </p>
""", unsafe_allow_html=True)
