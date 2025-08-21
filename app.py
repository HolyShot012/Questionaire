import streamlit as st
from model import CareerQuizModel

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
        border: 2px solid #A8E6CF;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)
model = CareerQuizModel(config_path="config.json", questions_csv_path="question.csv")

# Header
# st.image("banner.jpg", use_column_width=True)
st.title("Grow Your Path - Summer Dream: The Garden")

if "answers" not in st.session_state:
    st.session_state.answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "name" not in st.session_state:
    st.session_state.name = ""

st.header("Thông tin mở đầu")
st.subheader("Tên bạn là gì?")
st.session_state.name = st.text_input("Nhập tên của bạn", key="name_input")

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
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec['career_name']}")
        
        if st.button("Làm lại Quiz"):
            st.session_state.clear() 
            st.rerun()  
else:
    st.error("Không tải được câu hỏi. Vui lòng kiểm tra file question.csv.")