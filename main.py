import openai
import streamlit as st
from ratelimit import limits, RateLimitException, sleep_and_retry

# Initialize OpenAI with API key from Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Streamlit page configuration
st.set_page_config(
    page_title="Jürgens KI ChatBot",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="expanded",
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Hallo 👋")
    st.title("Ich bin Jürgen Wolf")

with col2:
    st.image("logo.png")

st.title(" ")

# Main content
st.write("Frag mich alles!")

# Sidebar
st.sidebar.title("Über mich")
st.sidebar.info(
    "Dieser Chatbot nutzt ChatGPT, um Ihre Fragen zu meinem Lebenslauf und weiteren Erfahrungen zu beantworten. "
    "Fragen Sie mich gerne nach meinen Fähigkeiten, Erfahrungen oder meinem beruflichen Werdegang!"
)

st.sidebar.title("Jürgen Wolf")
st.sidebar.info("Entdecken Sie mehr spannende Projekte und Tutorials.")

st.sidebar.title("Kontakt")
st.sidebar.info("Kontaktieren Sie mich für berufliche Möglichkeiten.")

# Load content from files
cv_path = "code.txt"  # Path to the CV file
additional_info_path = "info.txt"  # Path to the additional info file

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

# File upload feature
uploaded_file = st.sidebar.file_uploader("Laden Sie Ihr CV- oder Informationsdokument hoch", type=["txt"])
if uploaded_file:
    uploaded_content = uploaded_file.read().decode("utf-8")
    combined_content += f"\n\nHochgeladener Inhalt:\n{uploaded_content}"

# Rate limiting: Allow 5 requests per minute per user
ONE_MINUTE = 60
@sleep_and_retry
@limits(calls=5, period=ONE_MINUTE)
def get_chatgpt_response(prompt):
    try:
        # Update this part to match the new OpenAI API v1.0.0+ syntax
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Du bist ein Chatbot, der Fragen basierend auf Jürgen Wolfs Lebenslauf und zusätzlichen Informationen beantwortet:\n\n{combined_content}"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Fehler: {str(e)}"

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

# File download in sidebar
with st.sidebar:
    st.subheader("Lebenslauf herunterladen:")
    with open(cv_path) as f:
        st.download_button("Lebenslauf herunterladen", f, file_name="JürgenWolf_Lebenslauf.txt")
