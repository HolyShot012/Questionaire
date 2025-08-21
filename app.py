import streamlit as st
from model import CareerQuizModel
import qrcode
from io import BytesIO
import pandas as pd
import os
import gspread
from google.oauth2 import service_account

st.markdown("""
    <style>
    .main {
        background-color: #F5F5F5;
    }
    .stApp {
        max-width: 800px;
        margin: 0 auto;
        font-family: Arial, sans-serif;
    }
    h1, h2, h3 {
        color: #A8E6CF;
        text-align: center;
    }
    .stButton>button {
        background-color: #FF9999;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FF8080;
    }
    .stRadio>div>label {
        background-color: #A8E6CF33;
        padding: 8px;
        border-radius: 5px;
        margin-bottom: 5px;
    }
    .stTextInput>div>input {
        border: 3px solid #4CAF50;
        border-radius: 10px;
        background-color: #ffffff;
        padding: 10px;
        font-size: 16px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
    }
    .stTextInput>div {
        padding: 10px;
        border: 2px dashed #A8E6CF;
        border-radius: 12px;
        background-color: #FAFAFA;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

model = CareerQuizModel(config_path="config.json", questions_csv_path="question.csv")

st.title("Grow Your Path - Summer Dream: The Garden")

app_url = "https://holyshot012-questionaire-app-pqbsld.streamlit.app/"
qr = qrcode.make(app_url)
buf = BytesIO()
qr.save(buf, format="PNG")
st.image(buf.getvalue(), caption="Scan to open on your phone")

if "answers" not in st.session_state:
    st.session_state.answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "name" not in st.session_state:
    st.session_state.name = ""

st.header("Thông tin mở đầu")
st.subheader("Tên bạn là gì?")
st.session_state.name = st.text_input("Nhập tên của bạn", key="name_input")

def append_to_google_sheet(df):
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    client = gspread.authorize(creds)
    sh = client.open_by_key(st.secrets["gsheet_id"])
    try:
        ws = sh.worksheet(st.secrets.get("gsheet_tab", "Responses"))
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=st.secrets.get("gsheet_tab", "Responses"), rows="100", cols="10")
        ws.append_row(list(df.columns), value_input_option="USER_ENTERED")
    for _, row in df.iterrows():
        ws.append_row(row.tolist(), value_input_option="USER_ENTERED")

if model.questions:
    st.header("Tính cách")
    personality_questions = model.questions[:4]
    if len(personality_questions) < 4:
        st.warning(f"Chỉ tìm thấy {len(personality_questions)} câu hỏi cho phần Tính cách. Cần ít nhất 4 câu.")
    for question in personality_questions:
        st.subheader(f"Câu hỏi {question['id']}: {question['prompt']}")
        options = {key: option["text"] for key, option in question["options"].items()}
        answer = st.radio(
            f"Chọn đáp án cho câu hỏi {question['id']}",
            list(options.keys()),
            format_func=lambda x: options[x],
            key=f"q_{question['id']}",
            index=None
        )
        if answer:
            st.session_state.answers[question["id"]] = answer

    st.header("Kỹ năng")
    skills_questions = model.questions[4:8]
    if len(skills_questions) < 4:
        st.warning(f"Chỉ tìm thấy {len(skills_questions)} câu hỏi cho phần Kỹ năng. Cần ít nhất 4 câu.")
    for question in skills_questions:
        st.subheader(f"Câu hỏi {question['id']}: {question['prompt']}")
        options = {key: option["text"] for key, option in question["options"].items()}
        answer = st.radio(
            f"Chọn đáp án cho câu hỏi {question['id']}",
            list(options.keys()),
            format_func=lambda x: options[x],
            key=f"q_{question['id']}",
            index=None
        )
        if answer:
            st.session_state.answers[question["id"]] = answer

    st.header("Sở thích")
    interests_questions = model.questions[8:12]
    if len(interests_questions) < 4:
        st.warning(f"Chỉ tìm thấy {len(interests_questions)} câu hỏi cho phần Sở thích. Cần ít nhất 4 câu.")
    for question in interests_questions:
        st.subheader(f"Câu hỏi {question['id']}: {question['prompt']}")
        options = {key: option["text"] for key, option in question["options"].items()}
        answer = st.radio(
            f"Chọn đáp án cho câu hỏi {question['id']}",
            list(options.keys()),
            format_func=lambda x: options[x],
            key=f"q_{question['id']}",
            index=None
        )
        if answer:
            st.session_state.answers[question["id"]] = answer

    required_questions = [f"Q{i}" for i in range(1, 13)]
    all_answered = all(q_id in st.session_state.answers and st.session_state.answers[q_id] is not None for q_id in required_questions)
    if st.button("Gửi bài Quiz"):
        if not st.session_state.name:
            st.error("Vui lòng nhập tên của bạn trước khi gửi!")
        elif not all_answered:
            st.error("Vui lòng trả lời tất cả 12 câu hỏi trước khi gửi!")
        else:
            st.session_state.submitted = True

    if st.session_state.submitted and st.session_state.name:
        st.header("Lời cảm ơn")
        st.write(f"Cảm ơn {st.session_state.name} đã tham gia quiz Grow Your Path! Kết quả nghề nghiệp sẽ được AI model phân tích và hiển thị ngay tại booth.")
        scores = model.calculate_scores(st.session_state.answers)
        recommendations = model.get_recommendations(scores, top_n=3)
        st.subheader("Kết quả nghề nghiệp đề xuất")
        job_list = [rec['career_name'] for rec in recommendations]
        for i, job in enumerate(job_list, 1):
            st.write(f"{i}. {job}")
        new_data = pd.DataFrame([[st.session_state.name] + job_list], columns=["Name", "Job 1", "Job 2", "Job 3"])
        filename = "results.csv"
        if os.path.exists(filename):
            old = pd.read_csv(filename)
            updated = pd.concat([old, new_data], ignore_index=True)
        else:
            updated = new_data
        updated.to_csv(filename, index=False)
        append_to_google_sheet(new_data)
        if st.button("Làm lại Quiz"):
            st.session_state.clear()
            st.rerun()
else:
    st.error("Không tải được câu hỏi. Vui lòng kiểm tra file question.csv.")
