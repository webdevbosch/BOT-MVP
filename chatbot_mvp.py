import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import base64
from docx import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter

# Function to extract text from DOCX
def extract_text_from_docx(uploaded_file):
    doc = Document(uploaded_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Function to convert text to speech
def speak(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f'<audio controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

# Function to recognize speech
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language="en")
    except:
        return "Could not recognize speech."

# Streamlit UI - WhatsApp Style
st.markdown("""
    <style>
    .chat-container {
        display: flex;
        flex-direction: column;
        max-width: 400px;
        margin: auto;
    }
    .user-msg {
        background-color: #dcf8c6;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
        align-self: flex-end;
    }
    .bot-msg {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
        align-self: flex-start;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Bofalgan Chatbot")

uploaded_file = st.file_uploader("Upload Bofalgan document", type=["docx"])

if uploaded_file is not None:
    document_text = extract_text_from_docx(uploaded_file)
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(document_text)
    vectorstore = FAISS.from_texts(chunks, OpenAIEmbeddings())
    st.session_state["vectorstore"] = vectorstore
    st.write("Document uploaded successfully! Ask your questions.")

st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

query = st.text_input("Type your message:")
if st.button("Send"):
    if "vectorstore" in st.session_state:
        docs = st.session_state["vectorstore"].similarity_search(query, k=1)
        response = docs[0].page_content if docs else "Sorry, I couldn't find an answer."
        st.markdown(f"<div class='user-msg'>{query}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='bot-msg'>{response}</div>", unsafe_allow_html=True)
        speak(response, lang="en")
    else:
        st.write("Upload the document first.")

if st.button("🎤 Speak"):
    query = listen()
    st.write(f"You: {query}")
    if "vectorstore" in st.session_state:
        docs = st.session_state["vectorstore"].similarity_search(query, k=1)
        response = docs[0].page_content if docs else "Sorry, I couldn't find an answer."
        st.markdown(f"<div class='user-msg'>{query}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='bot-msg'>{response}</div>", unsafe_allow_html=True)
        speak(response, lang="en")
    else:
        st.write("Upload the document first.")

st.markdown("</div>", unsafe_allow_html=True)
