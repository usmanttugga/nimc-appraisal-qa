import streamlit as st
import json
import re
import base64
from rapidfuzz import fuzz, process

@st.cache_data
def load_questions():
    with open("questions.json", "r") as f:
        return json.load(f)

@st.cache_data
def load_logo():
    with open("logo.png", "rb") as f:
        return base64.b64encode(f.read()).decode()

def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^[\d]+[\.\)]\s*', '', text)
    text = re.sub(r'\b[a-d]\)\s*', ' ', text)
    text = re.sub(r'Answer:\s*[a-d]', '', text, flags=re.IGNORECASE)
    return text.strip()

def find_best_match(user_input, questions, threshold=55):
    cleaned_input = clean_text(user_input)
    if not cleaned_input:
        return None, 0
    question_texts = [clean_text(q["question"]) for q in questions]
    best_match = process.extractOne(
        cleaned_input,
        question_texts,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=threshold
    )
    if best_match:
        matched_text, score, index = best_match
        return questions[index], score
    return None, 0

def main():
    logo_b64 = load_logo()

    st.set_page_config(
        page_title="Data Protection MCQ Practice",
        page_icon=f"data:image/png;base64,{logo_b64}",
        layout="centered"
    )

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global - Obsidian Night */
    .stApp {
        background-color: #0B0F19 !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stApp > header { background-color: #0B0F19 !important; }
    .main .block-container {
        background-color: #0B0F19 !important;
        padding-top: 0.2rem !important;
        padding-bottom: 0rem !important;
    }

    /* Header */
    .app-header {
        text-align: center;
        padding: 0.5rem 1rem 0.2rem;
    }
    .app-header img {
        width: 45px;
        height: auto;
        margin-bottom: 0.2rem;
        filter: drop-shadow(0 0 12px rgba(99, 102, 241, 0.5));
        animation: pulse-glow 2s ease-in-out infinite;
    }
    @keyframes pulse-glow {
        0%, 100% { filter: drop-shadow(0 0 12px rgba(99, 102, 241, 0.5)); }
        50% { filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.8)); }
    }
    .app-header h1 {
        color: #E2E8F0;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        padding: 0;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .app-header p {
        color: #94A3B8;
        font-size: 0.9rem;
        margin: 0;
        padding: 0;
        line-height: 1.2;
    }

    /* Text area - Deep Slate */
    .stTextArea label {
        color: #CBD5E1 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
        padding: 1rem 1.2rem !important;
        font-size: 1rem !important;
        background-color: #1E293B !important;
        color: #E2E8F0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
        line-height: 1.6 !important;
    }
    .stTextArea textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.2), 0 2px 8px rgba(0,0,0,0.3) !important;
        outline: none !important;
    }
    .stTextArea textarea::placeholder {
        color: #64748B !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.65rem 1.5rem !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        border: none !important;
        color: #FFFFFF !important;
        background-color: #6366F1 !important;
        box-shadow: 0 2px 8px rgba(99,102,241,0.3) !important;
    }
    .stButton > button:hover {
        background-color: #4F46E5 !important;
        box-shadow: 0 4px 16px rgba(99,102,241,0.45) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:last-child {
        background-color: #1E293B !important;
        color: #94A3B8 !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:last-child:hover {
        background-color: #334155 !important;
        color: #E2E8F0 !important;
    }

    /* Answer card - Neon Lime glow */
    .answer-card {
        background: #1E293B;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 1px solid #334155;
        border-left: 5px solid #22C55E;
        box-shadow: 0 0 15px rgba(34, 197, 94, 0.15), 0 4px 20px rgba(0,0,0,0.3);
    }
    .answer-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #22C55E;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }
    .answer-text {
        font-size: 1.15rem;
        font-weight: 700;
        color: #22C55E;
        line-height: 1.5;
        text-shadow: 0 0 10px rgba(34, 197, 94, 0.3);
    }

    /* No match card */
    .no-match-card {
        background: #1E293B;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 1px solid #334155;
        border-left: 5px solid #F59E0B;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .no-match-text {
        font-size: 1rem;
        color: #FCD34D;
        font-weight: 500;
    }

    /* Browse section */
    .stExpander {
        border-radius: 10px !important;
        border: 1px solid #334155 !important;
        background-color: #1E293B !important;
    }
    .stExpander summary {
        color: #E2E8F0 !important;
    }
    .stExpander summary:hover {
        color: #6366F1 !important;
    }
    .stExpander details[open] {
        background-color: #1E293B !important;
    }
    .stExpander details[open] > div {
        background-color: #1E293B !important;
    }
    .stExpander .streamlit-expanderContent {
        background-color: #1E293B !important;
        color: #E2E8F0 !important;
    }
    .stTextInput label {
        color: #CBD5E1 !important;
        font-weight: 600 !important;
    }
    .stTextInput input {
        color: #E2E8F0 !important;
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
    }

    /* Streamlit expander content dark theme */
    .stExpander [data-testid="stMarkdownContainer"] {
        color: #E2E8F0 !important;
    }
    .stExpander [data-testid="stMarkdownContainer"] p {
        color: #E2E8F0 !important;
    }

    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #334155;
        margin: 1.5rem 0;
    }

    /* Caption */
    .stCaption, p.caption {
        color: #64748B !important;
    }

    /* Streamlit overrides for dark theme */
    .stMarkdown { color: #E2E8F0 !important; }
    h1, h2, h3, h4, h5, h6 { color: #E2E8F0 !important; }
    .stAlert > div { background-color: #1E293B !important; }

    /* Force dark background on all expander content */
    section[data-testid="stSidebar"] { background-color: #0B0F19 !important; }
    div[data-testid="stExpander"] { background-color: #1E293B !important; }
    div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] { color: #E2E8F0 !important; }

    /* Force dark on ALL Streamlit elements */
    .stApp, .stApp > div, .main, .block-container {
        background-color: #0B0F19 !important;
    }
    div[data-testid="stVerticalBlock"] {
        background-color: transparent !important;
    }
    section[data-testid="stSidebar"] > div {
        background-color: #0B0F19 !important;
    }
    .stDeployButton {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        background-color: #0B0F19 !important;
    }
    div[data-testid="stToolbar"] {
        background-color: #0B0F19 !important;
    }

    /* Fix white flash on mobile taps */
    * {
        -webkit-tap-highlight-color: transparent !important;
    }
    html, body {
        background-color: #0B0F19 !important;
        color: #E2E8F0 !important;
    }
    .stApp {
        background: #0B0F19 !important;
    }

    /* Force all expanders dark */
    details {
        background-color: #1E293B !important;
    }
    details[open] {
        background-color: #1E293B !important;
    }
    details > div {
        background-color: #1E293B !important;
    }

    /* Responsive - Mobile First */
    @media (max-width: 768px) {
        .app-header h1 { font-size: 1.4rem; }
        .app-header p { font-size: 0.9rem; }
        .answer-card { padding: 1.2rem; }
        .answer-text { font-size: 1rem; }
        .stTextArea textarea { padding: 0.9rem 1rem !important; font-size: 16px !important; }
        .option-row { font-size: 0.9rem; padding: 0.5rem 0.7rem; }
        .option-row.correct { font-size: 0.9rem; }

        /* Force dark on mobile */
        * {
            background-color: inherit !important;
        }
        .stApp, .block-container, main, section {
            background-color: #0B0F19 !important;
        }
        details, details[open], details > div, details[open] > div {
            background-color: #1E293B !important;
        }
        .app-header {
            padding: 0.2rem 0.5rem 0.1rem !important;
        }
        .app-header img {
            width: 35px !important;
            margin-bottom: 0.1rem !important;
        }
        .app-header h1 {
            font-size: 1.2rem !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .app-header p {
            font-size: 0.8rem !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .block-container {
            padding-top: 0.1rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="app-header">
        <img src="data:image/png;base64,{logo_b64}" alt="Logo">
        <h1>NIN Data Protection MCQ Practice</h1>
        <p>Paste a question to find the correct answer</p>
    </div>
    """, unsafe_allow_html=True)

    questions = load_questions()

    if "clear_pressed" not in st.session_state:
        st.session_state.clear_pressed = False
    if st.session_state.clear_pressed:
        st.session_state.user_input = ""
        st.session_state.clear_pressed = False

    user_input = st.text_area(
        "Paste a question below:",
        height=120,
        placeholder="e.g. What is personal data? Or paste any data protection question...",
        key="user_input",
        label_visibility="collapsed"
    )

    col_search, col_clear = st.columns([1, 1])
    with col_search:
        search_clicked = st.button("🔍 Search", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.clear_pressed = True
            st.rerun()

    if user_input:
        matched_question, score = find_best_match(user_input, questions)

        if matched_question:
            correct_option = matched_question["answer"]
            correct_text = matched_question["options"][correct_option]

            st.markdown(f"""
            <div class="answer-card">
                <div class="answer-label">Correct Answer</div>
                <div class="answer-text">The correct answer is; Option ({correct_option}) {correct_text}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("View full question details"):
                st.info(f"**Q{matched_question['id']}.** {matched_question['question']}")
                for key, val in matched_question["options"].items():
                    if key == correct_option:
                        st.success(f"**{key})** {val}  ✅")
                    else:
                        st.write(f"**{key})** {val}")
                st.caption(f"Match confidence: {score:.0f}%")
        else:
            st.markdown("""
            <div class="no-match-card">
                <div class="no-match-text">No matching question found. Try pasting a different snippet.</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    with st.expander("Browse All 100 Questions"):
        search_term = st.text_input("Search questions:", key="browse_search")
        filtered = questions
        if search_term:
            filtered = [q for q in questions if search_term.lower() in q["question"].lower()]
        for q in filtered:
            correct_option = q["answer"]
            correct_text = q["options"][correct_option]
            with st.expander(f"Q{q['id']}: {q['question'][:80]}..."):
                for key, val in q["options"].items():
                    if key == correct_option:
                        st.success(f"**{key})** {val}  ✅")
                    else:
                        st.write(f"**{key})** {val}")

if __name__ == "__main__":
    main()
