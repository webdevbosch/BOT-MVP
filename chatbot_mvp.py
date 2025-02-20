import streamlit as st
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
import speech_recognition as sr
from gtts import gTTS
import os
import base64
from docx import Document

# Function to extract text from the uploaded document
def extract_text_from_docx(uploaded_file):
    doc = Document(uploaded_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Function to convert text to speech and play it
def speak(text):
    tts = gTTS(text=text, lang="en")
    tts.save("response.mp3")
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
st.title("Bofalgan Chatbot")
st.write("Ask questions about Bofalgan!")

# Upload file
uploaded_file = st.file_uploader("Upload Bofalgan document (DOCX file)", type=["docx"])

if uploaded_file is not None:
    document_text = extract_text_from_docx(uploaded_file)
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(document_text)
    vectorstore = FAISS.from_texts(chunks, OpenAIEmbeddings())
    st.session_state["vectorstore"] = vectorstore
    st.write("Document uploaded successfully! Now you can ask questions.")

# Chat Interface
query = st.text_input("Ask something:")
if st.button("Submit"):
    if "vectorstore" in st.session_state:
        docs = st.session_state["vectorstore"].similarity_search(query, k=1)
        response = docs[0].page_content if docs else "Sorry, I couldn't find an answer in the document."
        st.markdown(f"**Chatbot:** {response}")
        speak(response)
    else:
        st.write("Please upload the document first.")

if st.button("Use Voice Input"):
    query = listen()
    st.write(f"**You:** {query}")
    if "vectorstore" in st.session_state:
        docs = st.session_state["vectorstore"].similarity_search(query, k=1)
        response = docs[0].page_content if docs else "Sorry, I couldn't find an answer in the document."
        st.markdown(f"**Chatbot:** {response}")
        speak(response)
    else:
        st.write("Please upload the document first.")
