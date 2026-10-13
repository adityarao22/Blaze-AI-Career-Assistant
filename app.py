import io
import requests
import streamlit as st
from pypdf import PdfReader

# =========================================================
# Blaze AI - STREAMLIT FRONTEND
# Backend: FastAPI at http://127.0.0.1:8000
# =========================================================

st.set_page_config(
    page_title="Blaze AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://127.0.0.1:8000"

# -------------------- SESSION STATE --------------------

DEFAULTS = {
    "resume_text": "",
    "resume_name": "",
    "resume_analysis": None,
    "interview_questions": [],
    "interview_role": "",
    "interview_type": "Technical",
    "interview_difficulty": "Beginner",
    "mock_started": False,
    "mock_current_index": 0,
    "mock_answers": [],
    "mock_completed": False,
    "job_match_result": None,
    "job_match_resume_name": "",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------- STYLING --------------------

st.markdown(
    """
    <style>
    .stApp {
        background: #0b1020;
        color: #edf2ff;
    }
    [data-testid="stSidebar"] {
        background: #11182b;
        border-right: 1px solid #27324b;
    }
    .brand {
        font-size: 27px;
        font-weight: 800;
        color: #c4b5fd;
        padding: 8px 0 2px 0;
    }
    .sidebar-caption {
        color: #a5b4fc;
        font-size: 10px;
        letter-spacing: 1.2px;
        margin-bottom: 22px;
    }
    .hero {
        padding: 22px 0 12px 0;
    }
    .hero h1 {
        font-size: 38px;
        line-height: 1.15;
        margin-bottom: 10px;
    }
    .muted {
        color: #aab4ca;
    }
    div[data-testid="stMetric"] {
        background: #151e33;
        border: 1px solid #27324b;
        padding: 16px;
        border-radius: 12px;
    }
    div[data-testid="stForm"] {
        border: 1px solid #27324b;
        border-radius: 12px;
        padding: 18px;
    }
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {
        border-radius: 9px;
        font-weight: 650;
    }
    /* Fix text visibility in input fields */
    .stTextArea textarea,
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] {
        color: #111827 !important;
        background-color: #ffffff !important;
        caret-color: #111827 !important;
    }
    
    /* Make placeholder text visible */
    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder {
        color: #6b7280 !important;
        opacity: 1 !important;
    }
    
    /* Improve labels and form text */
    .stTextArea label,
    .stTextInput label,
    .stSelectbox label {
        color: #f3f4f6 !important;
    }
    
    /* Keep typed answer text dark on white */
    .stTextArea textarea {
        -webkit-text-fill-color: #111827 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------- HELPERS --------------------

def api_post(endpoint, payload=None, files=None, timeout=120):
    """POST to the FastAPI backend and show useful error details."""
    try:
        if files is not None:
            response = requests.post(
                f"{API_URL}{endpoint}",
                files=files,
                timeout=timeout,
            )
        else:
            response = requests.post(
                f"{API_URL}{endpoint}",
                json=payload,
                timeout=timeout,
            )

        if not response.ok:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text

            st.error(
                f"API error ({response.status_code}) at {endpoint}: {detail}"
            )
            if response.status_code == 422:
                st.info(
                    "Check the request fields against the FastAPI model. "
                    "For interview generation, this app sends role, "
                    "interview_type, difficulty, num_questions, resume_text, "
                    "and job_description."
                )
            return None

        return response.json()

    except requests.ConnectionError:
        st.error(
            "Cannot connect to FastAPI. Start the backend in another "
            "terminal with: python -m uvicorn api:app --reload"
        )
    except requests.Timeout:
        st.error("The API request timed out. Please try again.")
    except requests.RequestException as exc:
        st.error(f"Request failed: {exc}")
    except ValueError:
        st.error("The API returned an invalid JSON response.")

    return None


def extract_pdf_text(uploaded_file):
    """Extract readable text from a PDF in Streamlit."""
    try:
        reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        return text.strip()
    except Exception as exc:
        st.error(f"Could not read the PDF: {exc}")
        return ""


def normalize_questions(raw_questions):
    """Normalize question responses to a list of dictionaries."""
    if isinstance(raw_questions, str):
        return [
            {"question": line.strip(), "sample_answer": ""}
            for line in raw_questions.splitlines()
            if line.strip()
        ]

    if not isinstance(raw_questions, list):
        return []

    normalized = []
    for item in raw_questions:
        if isinstance(item, str):
            normalized.append({
                "question": item,
                "sample_answer": "",
            })
        elif isinstance(item, dict):
            normalized.append({
                "question": item.get(
                    "question",
                    item.get("text", str(item)),
                ),
                "sample_answer": item.get(
                    "sample_answer",
                    item.get("answer", item.get("sample_answer", "")),
                ),
            })
        else:
            normalized.append({
                "question": str(item),
                "sample_answer": "",
            })

    return normalized


def download_text_button(label, filename, content, key):
    st.download_button(
        label=label,
        data=content,
        file_name=filename,
        mime="text/plain",
        key=key,
        use_container_width=True,
    )


def format_result(value):
    """Render API output whether it is a string, dictionary, or list."""
    if isinstance(value, (dict, list)):
        st.json(value)
    else:
        st.write(value)


# -------------------- SIDEBAR NAVIGATION --------------------

with st.sidebar:
    st.markdown(
        '<div class="brand">✦ Blaze AI</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-caption">YOUR PERSONAL AI CAREER ASSISTANT</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption("WORKSPACE")

    page = st.radio(
        "Navigate",
        [
            "📄 Resume Analysis",
            "🎯 Interview Preparation",
            "🎤 Mock Interview",
            "💼 Job Matching",
        ],
        label_visibility="collapsed",
        key="main_navigation",
    )

    st.divider()
    st.caption("SYSTEM STATUS")
    st.caption("FastAPI backend")
    st.caption("Groq AI integration")
    st.divider()
    st.caption("AI-generated career guidance")


# =========================================================
# PAGE 1: RESUME ANALYSIS
# =========================================================

if page == "📄 Resume Analysis":
    st.markdown(
        """
        <div class="hero">
            <h1>Make your resume work harder.</h1>
            <p class="muted">
                Upload your resume and get AI-powered career insights.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_resume = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"],
        key="resume_analysis_upload",
        help="Use a text-based PDF resume.",
    )

    job_description = st.text_area(
        "Target job description",
        key="resume_analysis_job_description",
        height=160,
        placeholder="Paste the job description you are targeting...",
    )

    if st.button(
        "✨ Analyze Resume",
        type="primary",
        key="analyze_resume_button",
        use_container_width=True,
    ):
        if uploaded_resume is None:
            st.warning("Please upload your resume PDF.")
        elif not job_description.strip():
            st.warning("Please enter the target job description.")
        else:
            with st.spinner("Uploading and analyzing your resume..."):
                upload_result = api_post(
                    "/upload-resume",
                    files={
                        "file": (
                            uploaded_resume.name,
                            uploaded_resume.getvalue(),
                            "application/pdf",
                        )
                    },
                )

                if upload_result and upload_result.get("text"):
                    resume_text = upload_result["text"].strip()
                    st.session_state.resume_text = resume_text
                    st.session_state.resume_name = uploaded_resume.name

                    analysis_result = api_post(
                        "/analyze-resume",
                        {
                            "resume_text": resume_text[:12000],
                            "job_description": job_description.strip()[:6000],
                        },
                    )

                    if analysis_result and analysis_result.get("success"):
                        st.session_state.resume_analysis = (
                            analysis_result.get("analysis", analysis_result)
                        )
                        st.success("Resume analysis completed!")

    if st.session_state.resume_analysis is not None:
        st.divider()
        st.subheader("📊 Resume Analysis Results")
        format_result(st.session_state.resume_analysis)
        download_text_button(
            "⬇️ Download Analysis",
            "blaze_resume_analysis.txt",
            str(st.session_state.resume_analysis),
            "download_resume_analysis",
        )

    if st.session_state.resume_text:
        st.caption(
            f"Stored resume: {st.session_state.resume_name or 'Uploaded PDF'}"
        )


# =========================================================
# PAGE 2: INTERVIEW PREPARATION
# =========================================================

elif page == "🎯 Interview Preparation":
    st.title("🎯 Interview Preparation")
    st.write(
        "Generate interview questions based on your target role, "
        "interview type, and difficulty."
    )

    with st.form("interview_generation_form"):
        role = st.text_input(
            "Target job role",
            value=st.session_state.interview_role,
            placeholder="e.g. ML Engineer, Data Analyst",
        )

        col1, col2 = st.columns(2)
        with col1:
            interview_type = st.selectbox(
                "Interview type",
                ["HR", "Technical", "Project-Based", "Mixed"],
                index=["HR", "Technical", "Project-Based", "Mixed"].index(
                    st.session_state.interview_type
                ),
            )
        with col2:
            difficulty = st.selectbox(
                "Difficulty level",
                ["Beginner", "Intermediate", "Advanced"],
                index=["Beginner", "Intermediate", "Advanced"].index(
                    st.session_state.interview_difficulty
                ),
            )

        num_questions = st.slider(
            "Number of questions",
            min_value=1,
            max_value=10,
            value=5,
        )

        interview_job_description = st.text_area(
            "Job description (optional)",
            placeholder="Paste the target job description here...",
            height=120,
        )

        generate = st.form_submit_button(
            "✨ Generate Interview Questions",
            type="primary",
            use_container_width=True,
        )

    if generate:
        if not role.strip():
            st.warning("Please enter a target job role.")
        else:
            payload = {
                "role": role.strip(),
                "interview_type": interview_type,
                "difficulty": difficulty,
                "num_questions": num_questions,
                "resume_text": st.session_state.resume_text[:8000],
                "job_description": interview_job_description.strip()[:4000],
            }

            with st.spinner("Generating interview questions..."):
                result = api_post("/generate-interview", payload)

            if result and result.get("success"):
                questions = normalize_questions(result.get("questions", []))
                if questions:
                    st.session_state.interview_questions = questions
                    st.session_state.interview_role = role.strip()
                    st.session_state.interview_type = interview_type
                    st.session_state.interview_difficulty = difficulty

                    # Reset mock interview for the new question set.
                    st.session_state.mock_started = False
                    st.session_state.mock_current_index = 0
                    st.session_state.mock_answers = []
                    st.session_state.mock_completed = False
                    st.success(f"Generated {len(questions)} questions.")
                else:
                    st.warning(
                        "The API response did not contain a questions list. "
                        "Check the response from generate_interview_questions()."
                    )

    questions = st.session_state.interview_questions

    if questions:
        st.divider()
        st.subheader("📝 Generated Questions")
        st.caption(
            f"Role: {st.session_state.interview_role} · "
            f"Type: {st.session_state.interview_type} · "
            f"Difficulty: {st.session_state.interview_difficulty}"
        )

        report_lines = []
        for i, item in enumerate(questions, start=1):
            question = item.get("question", "Question unavailable")
            sample_answer = item.get("sample_answer", "")

            with st.expander(f"Question {i}: {question}"):
                if sample_answer:
                    st.markdown("**Sample Answer**")
                    st.write(sample_answer)
                else:
                    st.info("No sample answer was returned for this question.")

            report_lines.append(
                f"Question {i}: {question}\n"
                f"Sample Answer: {sample_answer}\n"
            )

        download_text_button(
            "⬇️ Download Interview Questions",
            "blaze_interview_questions.txt",
            "\n".join(report_lines),
            "download_interview_questions",
        )


# =========================================================
# PAGE 3: MOCK INTERVIEW
# =========================================================

elif page == "🎤 Mock Interview":
    st.title("🎤 Mock Interview Mode")
    st.write(
        "Practice answering one question at a time, then review your answers."
    )

    questions = st.session_state.interview_questions

    if not questions:
        st.info(
            "First, open Interview Preparation and generate interview questions."
        )

    elif not st.session_state.mock_started:
        st.markdown(
            f"**Role:** {st.session_state.interview_role or 'Interview'}"
        )
        st.write(f"**Questions:** {len(questions)}")

        if st.button(
            "🚀 Start Mock Interview",
            type="primary",
            key="start_mock_interview",
        ):
            st.session_state.mock_started = True
            st.session_state.mock_current_index = 0
            st.session_state.mock_answers = [""] * len(questions)
            st.session_state.mock_completed = False
            st.rerun()

    elif not st.session_state.mock_completed:
        index = st.session_state.mock_current_index
        item = questions[index]
        question = item.get("question", "Question unavailable")

        st.progress(
            (index + 1) / len(questions),
            text=f"Question {index + 1} of {len(questions)}",
        )
        st.subheader(f"Question {index + 1}")
        st.write(question)

        with st.form(key=f"mock_answer_form_{index}"):
            answer = st.text_area(
                "Your answer",
                value=st.session_state.mock_answers[index],
                placeholder="Type your answer as you would in a real interview...",
                height=180,
            )
            submitted = st.form_submit_button(
                "Save Answer & Continue",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not answer.strip():
                st.warning("Please write an answer before continuing.")
            else:
                st.session_state.mock_answers[index] = answer.strip()

                if index + 1 < len(questions):
                    st.session_state.mock_current_index = index + 1
                else:
                    st.session_state.mock_completed = True

                st.rerun()

    else:
        st.success("🎉 You completed your mock interview!")
        st.subheader("Review Your Answers")

        report = []
        for i, item in enumerate(questions):
            question = item.get("question", "Question unavailable")
            answer = st.session_state.mock_answers[i]
            sample_answer = item.get("sample_answer", "")

            with st.expander(f"Question {i + 1}: {question}"):
                st.markdown("**Your answer**")
                st.write(answer or "(No answer)")
                if sample_answer:
                    st.markdown("**Suggested answer**")
                    st.write(sample_answer)

            report.append(
                f"Question {i + 1}: {question}\n"
                f"Your answer: {answer}\n"
                f"Suggested answer: {sample_answer}\n"
            )

        download_text_button(
            "⬇️ Download Mock Interview Report",
            "blaze_mock_interview.txt",
            "\n".join(report),
            "download_mock_interview",
        )

        if st.button(
            "🔄 Restart Mock Interview",
            key="restart_mock_interview",
        ):
            st.session_state.mock_started = False
            st.session_state.mock_current_index = 0
            st.session_state.mock_answers = []
            st.session_state.mock_completed = False
            st.rerun()


# =========================================================
# PAGE 4: JOB MATCHING
# =========================================================

elif page == "💼 Job Matching":
    st.title("💼 Job Matching")
    st.write(
        "Compare your resume with a job description using your existing "
        "resume-analysis AI function."
    )

    uploaded_job_resume = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"],
        key="job_matching_resume_upload",
    )

    if st.session_state.resume_text:
        st.caption(
            f"You can also use the previously uploaded resume: "
            f"{st.session_state.resume_name or 'Stored resume'}."
        )

    job_description = st.text_area(
        "Paste the job description",
        height=220,
        placeholder="Paste the complete job description here...",
        key="job_matching_description",
    )

    use_saved_resume = st.checkbox(
        "Use my previously uploaded resume if no new PDF is selected",
        value=True,
    )

    if st.button(
        "🔍 Match My Resume",
        type="primary",
        key="match_job_button",
        use_container_width=True,
    ):
        if uploaded_job_resume is not None:
            resume_text = extract_pdf_text(uploaded_job_resume)
            if resume_text:
                st.session_state.resume_text = resume_text
                st.session_state.resume_name = uploaded_job_resume.name
        elif use_saved_resume:
            resume_text = st.session_state.resume_text
        else:
            resume_text = ""

        if not resume_text:
            st.warning("Upload a text-readable PDF resume first.")
        elif not job_description.strip():
            st.warning("Please paste the job description.")
        else:
            with st.spinner("Analyzing your resume against the job..."):
                result = api_post(
                    "/match-job",
                    {
                        "resume_text": resume_text[:12000],
                        "job_description": job_description.strip()[:6000],
                    },
                )

            if result and result.get("success"):
                st.session_state.job_match_result = result.get(
                    "analysis",
                    result,
                )
                st.success("Job matching analysis completed!")

    if st.session_state.job_match_result is not None:
        st.divider()
        st.subheader("📊 Job Match Analysis")
    
        result = st.session_state.job_match_result
    
        if isinstance(result, dict):
            score = result.get("match_percentage", 0)
    
            st.metric(
                label="Estimated Resume–Job Match",
                value=f"{score}%"
            )
    
            st.progress(
                max(0.0, min(float(score) / 100, 1.0))
            )
    
            st.info(
                "This is an AI-generated estimate, "
                "not a validated hiring score."
            )
    
            st.markdown("### 📝 Match Summary")
            st.write(result.get("match_summary", "No summary available."))
    
            col1, col2 = st.columns(2)
    
            with col1:
                st.markdown("### ✅ Matched Skills")
                for skill in result.get("matched_skills", []):
                    st.markdown(f"- {skill}")
    
            with col2:
                st.markdown("### ⚠️ Missing Skills")
                for skill in result.get("missing_skills", []):
                    st.markdown(f"- {skill}")
    
            st.markdown("### 🎓 Matching Qualifications")
            for item in result.get("matching_qualifications", []):
                st.markdown(f"- {item}")
    
            st.markdown("### 📌 Qualification Gaps")
            for item in result.get("qualification_gaps", []):
                st.markdown(f"- {item}")
    
            st.markdown("### 💪 Your Strengths")
            for item in result.get("strengths", []):
                st.markdown(f"- {item}")
    
            st.markdown("### 🚀 Recommendations")
            for item in result.get("recommendations", []):
                st.markdown(f"- {item}")

    else:
        st.write(st.session_state.job_match_result)

    st.download_button(
        label="📥 Download Job Match Report",
        data=str(st.session_state.job_match_result),
        file_name="blaze_job_match_report.txt",
        mime="text/plain",
        key="download_job_match_report",
    )


# -------------------- FOOTER --------------------

st.divider()
st.caption(
    "✦ BLaze AI | Your Personal AI Career Assistant"
)
