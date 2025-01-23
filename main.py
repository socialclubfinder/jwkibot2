import streamlit as st
from openai import OpenAI
from collections import defaultdict, deque
import time

# Streamlit page configuration
st.set_page_config(page_title="Jürgens KI ChatBot", page_icon="💼")

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Load content from files
def load_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"Datei nicht gefunden: {file_path}")
        return ""

cv_content = load_file("code.txt")
additional_info_content = load_file("info.txt")

# Combine content for context
combined_content = f"{cv_content}\n\nZusätzliche Informationen:\n{additional_info_content}"

# Rate limit settings
RATE_LIMIT = 5  # Max messages
RATE_PERIOD = 120  # Time period in seconds (2 minutes)
user_activity = defaultdict(lambda: deque(maxlen=RATE_LIMIT))

def is_rate_limited(user_id):
    """Check if the user is rate-limited."""
    now = time.time()
    timestamps = user_activity[user_id]

    # Remove timestamps outside the rate limit period
    while timestamps and now - timestamps[0] > RATE_PERIOD:
        timestamps.popleft()

    # Check if the user exceeds the rate limit
    return len(timestamps) >= RATE_LIMIT

def get_chatgpt_response(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Du bist ein freundlicher Chatbot, der Fragen basierend auf Jürgen Wolfs Lebenslauf beantwortet:\n\n{combined_content}"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

# UI Layout
st.title("Jürgen Wolf")
st.sidebar.title("Über mich")
st.sidebar.info("Chatbot zu Jürgen Wolfs Lebenslauf")

# Get user identifier
user_id = st.session_state.get("user_id", st.session_state.session_id)

# Rate limit check
if is_rate_limited(user_id):
    st.error("Rate limit überschritten. Bitte warten Sie, bevor Sie weitere Fragen stellen.")
else:
    # Predefined questions
    predefined_questions = [
        "Was sind Jürgen Wolfs Hauptfähigkeiten?",
        "Wie sieht der Bildungshintergrund aus?",
        "Aktuelle Berufserfahrung?"
    ]

    st.subheader("Schnelle Fragen:")
    cols = st.columns(len(predefined_questions))
    for idx, question in enumerate(predefined_questions):
        if cols[idx].button(question, key=f"pred_q_{idx}"):
            user_activity[user_id].append(time.time())
            response = get_chatgpt_response(question)
            st.markdown(f"**Frage:** {question}")
            st.markdown(f"**Antwort:** {response}")

    # Custom user input
    with st.form(key="user_input_form"):
        user_input = st.text_input("Ihre Frage:")
        submit_button = st.form_submit_button(label="Fragen")

    if submit_button and user_input:
        user_activity[user_id].append(time.time())
        response = get_chatgpt_response(user_input)
        st.markdown(f"**Frage:** {user_input}")
        st.markdown(f"**Antwort:** {response}")
