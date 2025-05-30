# 🧠 Import all the tools we need to build the app!
import streamlit as st  # This helps us make a web app
from gtts import gTTS  # This turns text into robot speech
from io import BytesIO  # This helps us save sound in memory
from PIL import Image  # This helps us show pictures
import base64  # This turns pictures into code the AI understands
from openai import OpenAI  # This connects to the smart AI (ChatGPT)

# 🖥️ Set up the look and feel of our webpage
st.set_page_config(
    page_title="Open House Signbot",  # Title at the top
    page_icon="🏫",  # Little school emoji icon
    layout="wide"  # Stretch the layout wide
)

# 📦 These tools do different things:
# - streamlit lets us build the webpage.
# - gTTS turns words into voice.
# - BytesIO stores the voice in memory.
# - PIL helps with pictures.
# - base64 helps send pictures as special letters.
# - OpenAI talks to the AI assistant.

# 🎨 This makes the page look nice and wide with a cute icon and title.

# 🔐 Connect to OpenAI using a secret password (API key)
client = OpenAI(api_key=st.secrets["openai_api_key"])

# 🧠 This connects us to the ChatGPT brain using a secret password
# so it knows we are allowed to use it.

# ❓ These are some questions and answers already ready to go!
qa_pairs = {
    "Who is the principal": "Ms. Anne Yam",
    "Who is the vice principal": "Ms. Eleni Gardikiotis",
    "What subjects do you learn": "Math, science, Mandarin, French, coding, arts, Physical education, English language arts, social emotional learning, health and career education",
    "What are the school hours": "8:30 to 3:30 every day, except Wednesday: 8:30 to 2:30",
    "What sport events do you have": "Track and field, soccer, basketball, volleyball, badminton, cross country",
    "What clubs are there?": "Destination Imagination, choir, Afterschool sports, green club, leadership club"
}

# 📚 These are quick answers for common questions about the school.
# They help people learn without typing much!

# 🧠 Save information so we remember the chat and voice
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

if "image_audio_bytes" not in st.session_state:
    st.session_state.image_audio_bytes = None

# 💾 This keeps track of what people asked, what the robot said, and the sound files.
# It's like a memory box!

# 🔊 This turns words into a robot voice you can hear
def speak(text):
    tts = gTTS(text)  # Make the robot talk
    mp3_fp = BytesIO()  # Save the sound in memory
    tts.write_to_fp(mp3_fp)  # Write sound into memory
    return mp3_fp.getvalue()  # Return the sound to play

# 🗣️ This lets the robot say things out loud using a voice.

# 🖼️ This tells the AI to describe what it sees in a picture
def describe_image(image_data, prompt):
    base64_image = base64.b64encode(image_data).decode("utf-8")  # Turn picture into code
    response = client.chat.completions.create(
        model="gpt-4o",  # Use smart model
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }]
    )
    return response.choices[0].message.content.strip()

# 📷 This lets us send a picture to the AI and ask:
# "Can you describe this?" Then it tells us what it sees!

# 🧾 Add a big title and intro to the webpage
st.markdown("""
    <h1 style='text-align: center; color:#004466;'>🏫 Open House Assistant</h1>
    <p style='text-align: center; font-size:18px;'>Making school tours inclusive and informative for everyone.</p>
    <hr style='border-top: 2px solid #004466;'/>
""", unsafe_allow_html=True)

# 📢 This makes a fancy title and description at the top of the page.

# 🧱 Split the screen into two parts: left and right
col1, col2 = st.columns([3, 1.3], gap="large")

# 📏 This creates two columns:
# - Left side: Ask questions and chat
# - Right side: Take a picture and get help

# LEFT SIDE: Chat and Q&A
with col1:
    st.markdown("### 📝 Ask a Question")

    # Show all the messages you've asked and what the robot said
    with st.container(border=True):
        st.markdown("#### 💬 Chat History")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        if st.session_state.audio_bytes:
            st.audio(st.session_state.audio_bytes, format="audio/mp3")

    # 💬 This shows all the messages in the conversation so far.
    # If the robot gave a voice answer, you can hear it again!

    # 🧠 Buttons for quick questions
    st.markdown("#### Quick Questions")
    for question in qa_pairs.keys():
        if st.button(f"❓ {question}", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": question})
            answer = qa_pairs[question]
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.session_state.audio_bytes = speak(answer)
            st.rerun()

    # ✅ If you click a question, the robot answers right away.
    # You can hear the answer with a voice too!

    # 🧠 Ask your own question by typing
    st.markdown("#### Or ask something else:")
    user_input = st.text_input("Type your question here:")

    if st.button("💬 Send"):
        if user_input.strip() != "":
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            messages = [
                {"role": "system", "content": "You are an assistant helping visitors learn about Saint Francis Xavier School. Base your answers on information from https://sfxschool.ca."}
            ] + st.session_state.chat_history

            try:
                chat_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages
                )
                answer = chat_response.choices[0].message.content
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.session_state.audio_bytes = speak(answer)
                st.rerun()
            except Exception as e:
                st.error(f"Error generating answer: {e}")

    # 🧠 When you ask your own question, it talks to the AI and gives a new answer.

    # 🧹 Clear all the messages
    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.audio_bytes = None
        st.session_state.image_audio_bytes = None
        st.rerun()

    # 🧼 This button clears everything so you can start fresh.

# RIGHT SIDE: Camera Vision Station
with col2:
    st.markdown("### 📷 Visual Help Station")

    # Choose what kind of picture help you want
    mode = st.selectbox("Choose Mode:", [
        "🧠 Analyze Room",
        "🤟 Interpret ASL Letter",
        "👐 Interpret ASL Word"
    ])

    # 📸 Pick what you want to do:
    # - Analyze Room: describe the classroom or area
    # - ASL Letter: tell what hand sign you're making
    # - ASL Word: tell what word you're signing in ASL

    # 📷 Take a picture using the webcam
    picture = st.camera_input("Capture Image")

    if picture:
        st.image(picture, caption="📸 Image captured", use_container_width=True)

        with st.spinner("Processing image..."):
            try:
                image_data = picture.getvalue()

                # Pick the right question to ask AI
                if mode == "🧠 Analyze Room":
                    prompt = "Describe this image in detail to a visually impaired person."
                elif mode == "🤟 Interpret ASL Letter":
                    prompt = "What ASL letter is the person showing in this image? Only describe the letter being signed."
                elif mode == "👐 Interpret ASL Word":
                    prompt = "What ASL word or phrase is the person signing in this image? Be clear and concise in the interpretation."

                description = describe_image(image_data, prompt)

                st.markdown("**🧠 Description:**")
                st.markdown(description)

                st.session_state.image_audio_bytes = speak(description)
                st.audio(st.session_state.image_audio_bytes, format="audio/mp3")

            except Exception as e:
                st.error(f"❌ Error generating description: {e}")

    # 📷 This takes your picture, sends it to the AI, and gets a smart explanation.
    # It even reads it out loud for you!

# 🦶 Bottom of the page message
st.markdown("""
    <hr>
    <p style='text-align: center; font-size: 14px; color: gray;'>
        Built with ❤️ to support accessibility at school open houses.
    </p>
""", unsafe_allow_html=True)

# ❤️ A kind little message to show this was made to help everyone feel welcome.
