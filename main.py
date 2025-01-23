import streamlit as st
import openai
import os
from dotenv import load_dotenv
from ratelimit import limits, RateLimitException, sleep_and_retry

# Load environment variables from .env file
load_dotenv()

# Load content from files
cv_path = "code.txt"  # Path to the CV file
additional_info_path = "info.txt"  # Path to the additional info file


# Streamlit page configuration
st.set_page_config(
    page_title="Jürgens KI ChatBot",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="expanded",
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Hallo :wave:")
    st.title("Ich bin Jürgen Wolf")

with col2:
    st.image("logo.png")

st.title(" ")

#add
# Sidebar
st.sidebar.title("Jürgen Wolf")
st.sidebar.title("Über mich")
st.sidebar.info(
    "Dieser Chatbot nutzt ChatGPT, um Ihre Fragen zu meinem Lebenslauf und weiteren Erfahrungen zu beantworten. "
    "Fragen Sie mich gerne nach meinen Fähigkeiten, Erfahrungen oder meinem beruflichen Werdegang!"
)

st.sidebar.title("Kontakt")
st.sidebar.info("Kontaktieren Sie mich für berufliche Möglichkeiten.\n\n email: jurgenwo81@gmail.com")

# Sidebar - File download
with open(cv_path) as f:
    st.sidebar.download_button("Lebenslauf herunterladen", f, file_name="JürgenWolf_Lebenslauf.txt")


# API Key Management
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


def load_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"Datei nicht gefunden: {file_path}. Bitte überprüfen Sie den Dateipfad.")
        return ""

cv_content = load_file(cv_path)
additional_info_content = load_file(additional_info_path)

# Combine content from both files
combined_content = f"{cv_content}\n\nZusätzliche Informationen:\n{additional_info_content}"

# Rate limiting: Allow 5 requests per minute per user
ONE_MINUTE = 120
@sleep_and_retry
@limits(calls=5, period=ONE_MINUTE)
def get_chatgpt_response(prompt):
    try:
        # Überprüfung auf unangemessene oder irrelevante Fragen
        if not is_relevant_question(prompt):
            return "Entschuldigung, diese Frage ist unangemessen oder passt nicht zu meinen Aufgaben. Ich beantworte nur Fragen zu Jürgen Wolfs Lebenslauf und Erfahrungen."

        # Anfrage an OpenAI senden
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Du bist ein freundlicher und humorvoller Chatbot, der Fragen basierend auf Jürgen Wolfs Lebenslauf und zusätzlichen Informationen beantwortet:\n\n{combined_content}"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Fehler: {str(e)}"

# Hilfsfunktion zur Überprüfung der Relevanz der Frage
def is_relevant_question(prompt):
    relevant_keywords = [
        "Lebenslauf", "Erfahrungen", "Fähigkeiten", "Beruf", "Studium", 
        "Jürgen Wolf", "Karriere", "Projekte", "Programmieren", "Machine Learning", 
        "Web3", "Bildung", "FH", "Studienberechtigungsprüfung", "alter", "wohnort"
    ]
    # Überprüfen, ob die Frage relevante Schlüsselwörter enthält
    return any(keyword.lower() in prompt.lower() for keyword in relevant_keywords)


# Predefined questions
predefined_questions = [
    "Was sind Jürgen Wolfs Hauptfähigkeiten?",
    "Wie sieht der Bildungshintergrund von Jürgen Wolf aus?",
    "Was ist die aktuellste Berufserfahrung von Jürgen Wolf?",
    "Kannst du die zusätzlichen Erfolge von Jürgen Wolf zusammenfassen?"
]

# Predefined question buttons
st.subheader("Schnelle Fragen:")
cols = st.columns(len(predefined_questions))
for idx, question in enumerate(predefined_questions):
    if cols[idx].button(question, key=f"pred_q_{idx}"):
        try:
            response = get_chatgpt_response(question)
            st.markdown(f"**Frage:** {question}")
            st.markdown(f"**Antwort:** {response}")
            st.markdown("---")
        except RateLimitException:
            st.error("Rate limit überschritten. Bitte warten Sie einen Moment und versuchen Sie es erneut.")

# Custom user input
with st.form(key="user_input_form"):
    st.subheader("Stellen Sie Ihre eigene Frage:")
    user_input = st.text_input("Geben Sie Ihre Frage zu Jürgen Wolfs Lebenslauf und Erfahrungen ein:")
    submit_button = st.form_submit_button(label="Frage absenden")

if submit_button and user_input:
    try:
        response = get_chatgpt_response(user_input)
        st.markdown(f"**Frage:** {user_input}")
        st.markdown(f"**Antwort:** {response}")
        st.markdown("---")
    except RateLimitException:
        st.error("Rate limit überschritten. Bitte warten Sie einen Moment und versuchen Sie es erneut.")

# Previous conversations
if "conversations" not in st.session_state:
    st.session_state.conversations = []

if submit_button and user_input:
    st.session_state.conversations.append((user_input, response))

if st.session_state.conversations:
    st.subheader("Frühere Konversationen:")
    for q, a in reversed(st.session_state.conversations):
        st.markdown(f"**Frage:** {q}")
        st.markdown(f"**Antwort:** {a}")
        st.markdown("---")


