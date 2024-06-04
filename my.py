
import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import os
import fitz  # PyMuPDF for PDF files
import docx  # python-docx for DOCX files

# Google API Key for GenAI
GOOGLE_API_KEY = 'AIzaSyDlfQowL4ytEsQ8rBn6XJb1ED3QUCUksFo'
genai.configure(api_key=GOOGLE_API_KEY)

# Streamlit page configuration
st.set_page_config(page_title="Chatlop", page_icon="🤖", layout="wide")

# Prompt for GenAI
prompt = [
    """
    You are an expert in providing detailed and accurate answers to questions based on your vast knowledge. Answer the following questions to the best of your ability.
    """
]

# Function to retrieve response from GenAI for a given question
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

# Function to convert text to speech and play it
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    temp_fd, temp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(temp_fd)
    try:
        tts.save(temp_path)
        audio = AudioSegment.from_mp3(temp_path)
        play(audio)
    finally:
        os.remove(temp_path)

# Function to read content from an uploaded file
def read_uploaded_file(file):
    if file is not None:
        file_type = file.type
        if 'pdf' in file_type:
            return read_pdf(file)
        elif 'wordprocessingml' in file_type:
            return read_docx(file)
        else:
            st.write("Unsupported file type.")
            return None
    return None

# Function to read text from PDF file
def read_pdf(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

# Function to read text from DOCX file
def read_docx(file):
    doc = docx.Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Function to extract relevant content and get response from GenAI
def analyze_and_respond(file_content):
    response = get_gemini_response(file_content, prompt)
    return response

# Main function
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
            .button {
                background-color: black;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                transition-duration: 0.4s;
                cursor: pointer;
            }
            .button:hover {
                background-color: black;
                color: black;
                border: 2px solid black;
            }
            .file-content {
                background-color: black;
                padding: 10px;
                border-radius: 5px;
                margin-top: 10px;
            }
            .upload-section {
                background-color: black;
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
            }
            .upload-section input[type="file"] {
                background-color: black;
                color: black;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-title">Welcome to Chatlop</h1>', unsafe_allow_html=True)
    
    # Section 1: Chat with the Bot
    st.markdown('<h2 class="section-title">Chat with the Bot</h2>', unsafe_allow_html=True)
    user_input = st.text_input("Type your question here...")
    if st.button("Submit", key='chat_submit', help="Submit your question"):
        if user_input:
            response = get_gemini_response(user_input, prompt)
            if response:
                st.write(response)
                text_to_speech(response)
            else:
                st.write("No valid response could be generated.")
    
    # Section 2: File Upload
    st.markdown('<h2 class="section-title">Upload a File</h2>', unsafe_allow_html=True)
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
                    text_to_speech(response)
                else:
                    st.write("No valid response could be generated from the file content.")
        else:
            st.write("Please upload a file.")

app()
