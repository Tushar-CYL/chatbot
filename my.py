import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

# Google API Key for GenAI
GOOGLE_API_KEY = 'AIzaSyDlfQowL4ytEsQ8rBn6XJb1ED3QUCUksFo'
genai.configure(api_key=GOOGLE_API_KEY)

# Streamlit page configuration
st.set_page_config(page_title="DataNest", page_icon="🔎")

# Prompt for GenAI
prompt = [
    """
    You are an expert in providing concise and accurate answers to questions based on your vast knowledge. Answer the following questions to the best of your ability in three lines or less.
    """
]

# Function to retrieve response from GenAI for a given question
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

# Function to convert text to speech and play it
# def text_to_speech(text):
#     tts = gTTS(text=text, lang='en')
#     tts_bytes = tts.get_bytes()
#     play(AudioSegment.from_file(io.BytesIO(tts_bytes)))

# Main function
def app():
    st.title('Welcome to DataNest')
    st.subheader("What are you looking for?")

    recognizer = sr.Recognizer()

    st.write("Click the button and speak your query...")

    # Voice input button
    if st.button("Record Voice"):
        with sr.Microphone() as source:
            st.write("Listening...")
            audio_data = recognizer.listen(source)
            st.write("Recognizing...")
            try:
                question = recognizer.recognize_google(audio_data)
                st.write(f"Recognized: {question}")
                
                response = get_gemini_response(question, prompt)
                
                if response:
                    st.balloons()
                    st.write(response)
                    # text_to_speech(response)
                else:
                    st.write("No valid response could be generated.")
            except sr.UnknownValueError:
                st.write("Google Speech Recognition could not understand the audio.")
            except sr.RequestError as e:
                st.write(f"Could not request results from Google Speech Recognition service; {e}")

app()


# import streamlit as st
# import google.generativeai as genai
# import speech_recognition as sr
# from gtts import gTTS
# from pydub import AudioSegment
# from pydub.playback import play
# import io

# # Google API Key for GenAI
# GOOGLE_API_KEY = 'AIzaSyDlfQowL4ytEsQ8rBn6XJb1ED3QUCUksFo'
# genai.configure(api_key=GOOGLE_API_KEY)

# # Streamlit page configuration
# st.set_page_config(page_title="DataNest", page_icon="🔎")

# # Prompt for GenAI
# prompt = [
#     """
#     You are an expert in providing concise and accurate answers to questions based on your vast knowledge. Answer the following questions to the best of your ability in three lines or less.
#     """
# ]

# # Function to retrieve response from GenAI for a given question
# def get_gemini_response(question, prompt):
#     model = genai.GenerativeModel('gemini-pro')
#     response = model.generate_content([prompt[0], question])
#     return response.text

# # Function to convert text to speech and play it
# # def text_to_speech(text):
# #     tts = gTTS(text=text, lang='en')
# #     tts_bytes = tts.get_audio_data()
# #     play(AudioSegment.from_file(io.BytesIO(tts_bytes), format="mp3"))

# # Main function
# def app():
#     st.title('Welcome to DataNest')
#     st.subheader("What are you looking for?")

#     recognizer = sr.Recognizer()

#     st.write("Click the button and speak your query...")

#     # Voice input button
#     if st.button("Record Voice"):
#         with sr.Microphone() as source:
#             st.write("Listening...")
#             audio_data = recognizer.listen(source)
#             st.write("Recognizing...")
#             try:
#                 question = recognizer.recognize_google(audio_data)
#                 st.write(f"Recognized: {question}")
                
#                 response = get_gemini_response(question, prompt)
                
#                 if response:
#                     st.write(response)
#                     # text_to_speech(response)
#                 else:
#                     st.write("No valid response could be generated.")
#             except sr.UnknownValueError:
#                 st.write("Google Speech Recognition could not understand the audio.")
#             except sr.RequestError as e:
#                 st.write(f"Could not request results from Google Speech Recognition service; {e}")

# app()










# no button listning all time
# 
# 
# 
# 

# import streamlit as st
# import google.generativeai as genai
# import speech_recognition as sr

# # Google API Key for GenAI
# GOOGLE_API_KEY = 'AIzaSyDlfQowL4ytEsQ8rBn6XJb1ED3QUCUksFo'
# genai.configure(api_key=GOOGLE_API_KEY)

# # Streamlit page configuration
# st.set_page_config(page_title="ArtifactExplorer", page_icon="🔎")

# # Prompt for GenAI
# prompt = [
#     """
#     You are an expert in providing concise and accurate answers to questions based on your vast knowledge. Answer the following questions to the best of your ability in three lines or less.
#     """
# ]

# # Function to retrieve response from GenAI for a given question
# def get_gemini_response(question, prompt):
#     model = genai.GenerativeModel('gemini-pro')
#     response = model.generate_content([prompt[0], question])
#     return response.text

# # Main function
# def app():
#     st.title('Welcome to ArtifactExplorer')
#     st.subheader("Whats on your mind? Any Doubt , feel free to ask!!")

#     recognizer = sr.Recognizer()

#     st.write("Speak your doubt aloud.....")

#     # Continuous listening and answering loop
#     while True:
#         with sr.Microphone() as source:
#             st.write("Listening to you...")
#             audio_data = recognizer.listen(source)
#             st.write("Recognizing your voice...")
#             try:
#                 question = recognizer.recognize_google(audio_data)
#                 st.write(f"Recognized: {question}")
                
#                 response = get_gemini_response(question, prompt)
                
#                 if response:
#                     st.write(response)
#                 else:
#                     st.write("No valid response could be generated.")
#             except sr.UnknownValueError:
#                 st.write("Bot Speech Recognition could not understand the audio.")
#             except sr.RequestError as e:
#                 st.write(f"Could not request results from Bot Speech Recognition service; {e}")

# app()
