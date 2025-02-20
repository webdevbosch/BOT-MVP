import streamlit as st
from langchain.llms import OpenAI
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import speech_recognition as sr
from gtts import gTTS
import os
import base64

# Function to convert text to speech and play it
def speak(text):
    tts = gTTS(text=text, lang="en")
    tts.save("response.mp3")

    # Provide a link to download and play audio
    with open("response.mp3", "rb") as f:
        audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    
    audio_html = f'''
    <audio controls>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Your browser does not support audio playback.
    </audio>
    '''
    st.markdown(audio_html, unsafe_allow_html=True)

# Function to convert speech to text
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language="en")
    except sr.UnknownValueError:
        return "Could not understand audio."
    except sr.RequestError:
        return "Speech recognition service error."

# Streamlit UI
st.title("AI Chatbot with Literature")

# Upload file
uploaded_file = st.file_uploader("Upload your literature (TXT file)", type=["txt"])

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    st.session_state["document"] = content
    st.write("Document uploaded successfully!")

query = st.text_input("Ask something:")

if st.button("Submit"):
    if "document" in st.session_state:
        # Using a basic retrieval mechanism (Replace with FAISS/Embeddings for better performance)
        response = "Relevant answer based on uploaded literature."
        st.write(response)
        speak(response)
    else:
        st.write("Please upload a document first.")

if st.button("Use Voice Input"):
    query = listen()
    st.write(f"You said: {query}")
