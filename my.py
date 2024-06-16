import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF for PDF files
import docx  # python-docx for DOCX files
import sqlite3

# Google API Key for GenAI
GOOGLE_API_KEY = 'AIzaSyDlfQowL4ytEsQ8rBn6XJb1ED3QUCUksFo'
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize database
def init_db():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS file_analysis (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            content TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Save a chat message to the database
def save_message(role, content):
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (role, content) VALUES (?, ?)', (role, content))
    conn.commit()
    conn.close()

# Retrieve all chat messages from the database
def get_all_messages():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('SELECT role, content FROM messages ORDER BY timestamp')
    messages = c.fetchall()
    conn.close()
    return messages

# Save a file analysis result to the database
def save_file_analysis(filename, content, response):
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('INSERT INTO file_analysis (filename, content, response) VALUES (?, ?, ?)', (filename, content, response))
    conn.commit()
    conn.close()

# Retrieve all file analysis results from the database
def get_file_analyses():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('SELECT filename, content, response FROM file_analysis ORDER BY timestamp')
    analyses = c.fetchall()
    conn.close()
    return analyses

# Define prompt
prompt = [
    """
    You are an expert in providing detailed and accurate answers to questions based on your vast knowledge. Answer the following questions to the best of your ability.
    """
]

# Function to retrieve response from GenAI for a given question
def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt[0], question])
        return response.text
    except Exception as e:
        st.error(f"Error getting response from GenAI: {e}")
        return None

# Function to read content from an uploaded file
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

# Function to read text from PDF file
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

# Function to read text from DOCX file
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
            for role, content in get_all_messages():
                st.session_state["messages"].append({"role": role, "content": content})
        
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
        
        if user_input := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)
            save_message("user", user_input)
            response = get_gemini_response(user_input, prompt)
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.chat_message("assistant").write(response)
                save_message("assistant", response)
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
                        save_file_analysis(uploaded_file.name, file_content, response)
                    else:
                        st.error("No valid response could be generated from the file content.")
            else:
                st.error("Please upload a file.")
    
    elif option == 'History':
        st.markdown('<h2 class="section-title">History 📜</h2>', unsafe_allow_html=True)
        st.write("Chat History:")
        messages = get_all_messages()
        for role, content in messages:
            st.markdown(f"**{role.capitalize()}**: {content}")
        st.write("File Analysis History:")
        analyses = get_file_analyses()
        for filename, content, response in analyses:
            st.markdown(f"**File**: {filename}")
            st.markdown(f"**Content**: {content}")
            st.markdown(f"**Response**: {response}")

app()
