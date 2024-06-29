import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import os
import fitz  # PyMuPDF for PDF files
import docx  # python-docx for DOCX files
from pymongo import MongoClient
from datetime import datetime

# MongoDB setup
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client.chatlop_db
collection = db.conversations

GOOGLE_API_KEY = 'AIzaSyDlfQowL4ytEsQ8rBn6XJb1ED3QUCUksFo'
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Chatlop", page_icon="🤖", layout="wide")

prompt = [
"""
You are an expert in providing detailed and accurate answers to questions based on your vast knowledge. Answer the following questions to the best of your ability.
"""
]

def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt[0], question])
        return response.text
    except Exception as e:
        st.error(f"Error getting response from GenAI: {e}")
        return None

def read_uploaded_file(file):
    try:
        if file is not None:
            file_type = file.type
            if 'pdf' in file_type:
                return read_pdf(file)
            elif 'wordprocessingml' in file_type:
                return read_docx(file)
            else:
                st.error("Unsupported file type.")
                return None
        return None
    except Exception as e:
        st.error(f"Error reading uploaded file: {e}")
        return None

def read_pdf(file):
    try:
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return ""

def read_docx(file):
    try:
        doc = docx.Document(file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        st.error(f"Error reading DOCX file: {e}")
        return ""

def analyze_and_respond(file_content):
    response = get_gemini_response(file_content, prompt)
    return response

def save_to_mongo(data):
    try:
        collection.insert_one(data)
    except Exception as e:
        st.error(f"Error saving to MongoDB: {e}")

def app():
    st.markdown("""
    <style>
    .main-title {
        font-family: 'Arial', sans-serif;
        color: #2E4053;
        text-align: center;
        margin-bottom: 20px;
    }
    .section-title {
        font-family: 'Arial', sans-serif;
        color: white;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-title">Welcome to Chatlop</h1>', unsafe_allow_html=True)

    option = st.sidebar.selectbox(
        'Choose an option',
        ['Chat with Bot', 'Upload Document', 'History']
    )

    if option == 'Chat with Bot':
        st.markdown('<h2 class="section-title">Chat with the Bot 🤖</h2>', unsafe_allow_html=True)
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
        
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
        
        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            response = get_gemini_response(prompt, prompt)
            if response:
                msg = response
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.chat_message("assistant").write(msg)
                # Save conversation to MongoDB
                save_to_mongo({
                    "timestamp": datetime.now(),
                    "user_message": prompt,
                    "bot_response": msg
                })
            else:
                st.error("No valid response could be generated.")

    elif option == 'Upload Document':
        st.markdown('<h2 class="section-title">Upload a File 📔</h2>', unsafe_allow_html=True)
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Analyze File", key='file_analyze', help="Analyze the uploaded file"):
            if uploaded_file:
                file_content = read_uploaded_file(uploaded_file)
                if file_content:
                    response = analyze_and_respond(file_content)
                    if response:
                        st.markdown('<div class="file-content">{}</div>'.format(response), unsafe_allow_html=True)
                        # Save file analysis to MongoDB
                        save_to_mongo({
                            "timestamp": datetime.now(),
                            "file_name": uploaded_file.name,
                            "file_content": file_content,
                            "analysis_response": response
                        })
                    else:
                        st.error("No valid response could be generated from the file content.")
            else:
                st.error("Please upload a file.")

    elif option == 'History':
        st.markdown('<h2 class="section-title">History 📜</h2>', unsafe_allow_html=True)
        history = list(collection.find().sort("timestamp", -1))
        if history:
            for record in history:
                st.write(f"Timestamp: {record['timestamp']}")
                if "user_message" in record:
                    st.write(f"User: {record['user_message']}")
                    st.write(f"Bot: {record['bot_response']}")
                if "file_name" in record:
                    st.write(f"File: {record['file_name']}")
                    st.write(f"File Content: {record['file_content']}")
                    st.write(f"Analysis: {record['analysis_response']}")
                st.write("---")
        else:
            st.write("No history available.")

app()
