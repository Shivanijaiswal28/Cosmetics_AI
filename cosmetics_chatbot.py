import streamlit as st
import mysql.connector
from openai import AzureOpenAI
import os
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import tempfile
import speech_recognition as sr
import io
import base64
from pydub import AudioSegment
from pydub.utils import which

# If ffmpeg is not in PATH, uncomment and set the correct path:
# AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"

# -----------------------------
# Initialize Gemini client
# -----------------------------
# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-05-01-preview",   # latest stable
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")


# -----------------------------
# Connect to MySQL
# -----------------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="shivani28",
    database="cosmetics_db"
)
cursor = db.cursor(dictionary=True)

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("SHIVANI'S Cosmetics Advisor Ai 💕")

if 'history' not in st.session_state:
    st.session_state.history = []

# -----------------------------
# Helper: normalize mic_recorder output to bytes
# -----------------------------
def get_audio_bytes_from_micrecorder(voice):
    if not voice:
        return None

    # case: voice is a dict like {"bytes": "<base64 string>"}
    if isinstance(voice, dict):
        # common keys: "bytes", "audio", "blob"
        for key in ("bytes", "audio", "blob"):
            if key in voice and voice[key]:
                val = voice[key]
                if isinstance(val, str):
                    # handle data-url e.g. "data:audio/wav;base64,...."
                    if val.startswith("data:"):
                        try:
                            header, b64 = val.split(",", 1)
                            return base64.b64decode(b64)
                        except Exception:
                            pass
                    # plain base64 string
                    try:
                        return base64.b64decode(val)
                    except Exception:
                        pass
                elif isinstance(val, (bytes, bytearray)):
                    return bytes(val)
    # case: voice is a plain base64 string
    if isinstance(voice, str):
        if voice.startswith("data:"):
            try:
                header, b64 = voice.split(",", 1)
                return base64.b64decode(b64)
            except Exception:
                return None
        try:
            return base64.b64decode(voice)
        except Exception:
            return None
    # case: voice is bytes already
    if isinstance(voice, (bytes, bytearray)):
        return bytes(voice)

    return None

# -----------------------------
# Convert audio bytes -> text (using pydub -> WAV -> speech_recognition)
# -----------------------------
def audio_to_text(audio_bytes):
    if not audio_bytes:
        return ""

    recognizer = sr.Recognizer()
    audio_file = io.BytesIO(audio_bytes)

    try:
        # pydub autodetects format from header
        audio = AudioSegment.from_file(audio_file)
    except Exception as e:
        st.error(f"Could not decode audio (need ffmpeg installed and in PATH). Error: {e}")
        return ""

    # Normalize to PCM WAV, 16 kHz, mono, 16-bit
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
        audio.export(tmp_wav.name, format="wav")
    try:
        with sr.AudioFile(tmp_wav.name) as source:
            audio_data = recognizer.record(source)
            try:
                return recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                return ""
            except sr.RequestError as e:
                st.error(f"Speech Recognition error: {e}")
                return ""
    finally:
        try:
            os.remove(tmp_wav.name)
        except Exception:
            pass

# -----------------------------
# 🎤 Voice or Text Input
# -----------------------------
st.subheader("🎤 Speak or type your query")
voice = mic_recorder(start_prompt="🎙️ Start Recording", stop_prompt="⏹️ Stop Recording")

user_input = ""
if voice:
    # Convert whatever mic_recorder returned into raw bytes
    audio_bytes = get_audio_bytes_from_micrecorder(voice)
    if audio_bytes:
        user_input = audio_to_text(audio_bytes).strip()
        if not user_input:
            st.warning("⚠️ Could not recognize speech. Please try again or type your query.")
    else:
        st.warning("⚠️ Unrecognized microphone output format.")
else:
    user_input = st.text_input("Or type your query:")

# -----------------------------
# Fetch products from MySQL
# -----------------------------
def fetch_products(category=None):
    if category:
        cursor.execute("SELECT * FROM products WHERE category=%s AND stock>0", (category,))
    else:
        cursor.execute("SELECT * FROM products WHERE stock>0")
    return cursor.fetchall()

# -----------------------------
# Generate AI response
# -----------------------------
def generate_response(user_msg):
    products = fetch_products()
    product_list = "\n".join([f"{p['name']} ({p['brand']}, {p['shade']}) - ₹{p['price']}" for p in products])

    prompt = f"""
    You are a cosmetics expert. User asked: "{user_msg}".
    Here is a list of available products:
    {product_list}
    Suggest the most suitable products for the user with explanation.
    """

    response = client.chat.completions.create(
        model=deployment_name,  # Your Azure deployment name
        messages=[
            {"role": "system", "content": "You are a helpful cosmetics expert AI assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


# -----------------------------
# Handle user input
# -----------------------------
if st.button("Send") and user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    ai_response = generate_response(user_input)
    st.session_state.history.append({"role": "ai", "content": ai_response})

    # 🔊 Convert AI response to speech
    tts = gTTS(ai_response, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts.save(tmp_file.name)
        st.audio(tmp_file.name, format="audio/mp3")

# -----------------------------
# Display chat history
# -----------------------------
for chat in st.session_state.history:
    if chat["role"] == "user":
        st.markdown(f"**You:** {chat['content']}")
    else:
        st.markdown(f"**AI:** {chat['content']}")
