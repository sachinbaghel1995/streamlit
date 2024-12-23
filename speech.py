import openai
import pyttsx3
import streamlit as st
from threading import Thread
from queue import Queue
import time

# OpenAI API Key
openai.api_key = "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"

# Initialize pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 200)  # Increase speech rate

def set_voice_by_id(voice_id):
    voices = engine.getProperty('voices')
    for voice in voices:
        if voice.id == voice_id:
            engine.setProperty('voice', voice.id)
            break

# Set voice to Microsoft Zira (Female)
set_voice_by_id("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0")

# Function to greet Muskan on startup
@st.cache_resource
def greet_muskan():
    greeting = "Happy Birthday Muskan, the most beautiful person in the world!"
    st.write(greeting)
    speak_text(greeting)

# System prompt
SYSTEM_PROMPT = """
You are a chatbot designed for Muskan, created by Sachin to make her birthday special. Engage her with fun questions, nostalgic references, and heartfelt messages.

Instructions:
- Respond warmly and enthusiastically.
- Ask questions about shared memories and validate her answers.
- Always respond with humor or appreciation to create an engaging experience.
"""

# Initialize conversation history
conversation_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

# Define questions and correct answers
questions_answers = [
    {
        "question": "During the dare game, what color dare did Muskan assign to Sachin?",
        "answer": "Violet",
        "correct": "You really love Sachin! ❤️",
        "incorrect": "Sachin loves you more! 😍"
    },
    {
        "question": "What poetic phrase did Muskan use to describe her 'darshan ka time'?",
        "answer": "प्रत्येक कार्य अपने समय पर होता है जैसे पौधों मे फूल और फल समय पर आते है",
        "correct": "Wow, you remember everything! 🥰",
        "incorrect": "Sachin might remember this better, he loves you endlessly. 💖"
    },
    {
        "question": "What food item did Sachin joke about making in his dreams?",
        "answer": "Khyali Jalebi",
        "correct": "Perfect answer! You know each other too well. ✨",
        "incorrect": "Sachin will cook up something memorable for you someday! 🥰"
    },
     {
        "question": "What did you once say about how you describe Muskan and Sachin together in three words?",
        "answer": "Most expensive painting",
        "correct": "Beautifully said! You both are priceless together. 🎨",
        "incorrect": "Sachin thinks every word from you is art! ❤️"
    },
    {
        "question": "What was your reply to Sachin when he asked if you remembered his birthday?",
        "answer": "Koi muzse neend me uthakar puche na to bhi me bta skti hu *1 nov 1996* was the day when my precious gem entered this world.",
        "correct": "You’ve got an incredible memory! ❤️",
        "incorrect": "Sachin knows you’ll never forget his special day! 🌟"
    }
]

# Function to generate assistant response
def generate_response(prompt, response_queue):
    global conversation_history
    conversation_history.append({"role": "user", "content": prompt})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=conversation_history,
            max_tokens=150,  # Limit tokens to reduce response time
            n=1,
            temperature=0.7,
        )
        assistant_response = response["choices"][0]["message"]["content"]
        conversation_history.append({"role": "assistant", "content": assistant_response})
        response_queue.put(assistant_response)
    except Exception as e:
        response_queue.put(f"Error: {e}")

# Text-to-speech function
def speak_text(text):
    try:
        engine.stop()  # Stop any ongoing speech
        engine.say(text)
        engine.runAndWait()
    except RuntimeError as e:
        print(f"Runtime Error during speech synthesis: {e}")

# Streamlit app
st.title("I love You My Cutie")
st.write("Welcome, Muskan! Ready for a memorable experience?")

# Greet Muskan on app start
if "greeted" not in st.session_state:
    st.session_state["greeted"] = False

if not st.session_state["greeted"]:
    greet_muskan()
    st.session_state["greeted"] = True

# Input field for user queries
user_input = st.text_input("Enter your query or answer the questions below:")
response_placeholder = st.empty()
question_placeholder = st.empty()

# Response queue for threading
response_queue = Queue()

# Ask a question
if "question_index" not in st.session_state:
    st.session_state["question_index"] = 0

if user_input:
    response_thread = Thread(target=generate_response, args=(user_input, response_queue))
    response_thread.start()

    with st.spinner("Processing your request..."):
        response_thread.join()

    if not response_queue.empty():
        assistant_response = response_queue.get()
        response_placeholder.write(f"Assistant: {assistant_response}")
        speak_text(assistant_response)

        # Reset conversation history if order is complete
        if "order has been confirmed" in assistant_response.lower():
            conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
            st.success("Thank you for your order! If you need anything else, let us know.")

# Display the current question
if st.session_state["question_index"] < len(questions_answers):
    current_question = questions_answers[st.session_state["question_index"]]
    question_placeholder.write(f"Question: {current_question['question']}")

    if user_input:
        if user_input.lower() == current_question['answer'].lower():
            st.success(current_question['correct'])
        else:
            st.warning(current_question['incorrect'])

        # Move to the next question
        st.session_state["question_index"] += 1

        if st.session_state["question_index"] < len(questions_answers):
            next_question = questions_answers[st.session_state["question_index"]]
            question_placeholder.write(f"Next Question: {next_question['question']}")
        else:
            question_placeholder.write("You have completed all the questions! 🎉")
            st.balloons()
else:
    question_placeholder.write("You have completed all the questions! 🎉")

