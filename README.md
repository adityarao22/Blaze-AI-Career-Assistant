# 🚀 Blaze — AI Career Assistant


## 📌 Overview

**Blaze — AI Career Assistant** is a Generative AI application designed to make career preparation more organized, personalized, and accessible.

Job seekers often struggle to identify gaps in their resumes, understand job requirements, and prepare for technical interviews. Blaze brings these activities together in a single interface.

The application combines a Streamlit frontend, a FastAPI backend, and Groq-powered language model capabilities to provide personalized career guidance.

## ✨ Key Features

### 1. 📄 Resume Analysis

Analyze a text-based PDF resume and obtain AI-generated career insights.

- Extract text from a resume PDF.
- Review skills, projects, and experience.
- Identify strengths and potential improvement areas.
- Receive suggestions to improve resume relevance.
- Generate personalized career recommendations.

**Goal:** Help candidates understand how to present their qualifications more effectively.

### 2. 🎯 Job Matching

Compare a candidate's resume against a target job description.

- Analyze the resume and job requirements.
- Identify matching technical skills.
- Highlight missing or insufficiently demonstrated skills.
- Generate a match score when supported by the analysis.
- Provide recommendations for improving job alignment.

**Example:** For a Data Analyst position, the application may identify Python, SQL, and Pandas as matching skills while highlighting Power BI or data visualization as areas to strengthen, depending on the resume and job description.

> AI-generated match scores are estimates, not guarantees of hiring success.

### 3. 💼 Interview Preparation

Generate interview practice material tailored to a selected role.

- Choose a target job role.
- Select an interview category.
- Choose a difficulty level.
- Generate relevant interview questions.
- Review sample answers and explanations.
- Use the questions to revise important concepts.

This feature can support preparation for technical and entry-level interviews.

### 4. 🎤 Mock Interview Mode

Practice answering interview questions in a simulated interview workflow.

- Practice questions relevant to the selected role.
- Attempt answers before reviewing suggested responses.
- Compare your answers with sample answers or evaluation feedback when supported by the application.
- Identify topics that need further revision.
- Improve confidence through repeated practice.

Mock interview feedback is intended for learning and practice; it does not guarantee actual interview performance.

---

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web interface |
| FastAPI | Backend API and request handling |
| Groq API | Generative AI model access |
| PDF processing library | Extracting text from PDF resumes |
| Uvicorn | Running the FastAPI server |
| Git | Version control |
| GitHub | Source code hosting and portfolio presentation |

**Note:** The exact model, PDF library, and additional dependencies are defined by the project's implementation and `requirements.txt`.

---

## 🏗️ Application Architecture

```text
                   ┌──────────────────────┐
                   │        User          │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │   Streamlit UI       │
                   │       app.py         │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │    FastAPI Backend   │
                   │       api.py         │
                   └──────────┬───────────┘
                              │
                 ┌────────────┴─────────────┐
                 ▼                          ▼
      ┌────────────────────┐    ┌────────────────────┐
      │ PDF Text Extraction│    │ Interview / Job    │
      │ pdf_processor.py   │    │ Logic              │
      └──────────┬─────────┘    │ interview.py       │
                 │              └─────────┬──────────┘
                 └────────────┬───────────┘
                              ▼
                   ┌──────────────────────┐
                   │     Groq API         │
                   │   Language Model     │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Generated Insights,  │
                   │ Questions & Feedback  │
                   └──────────────────────┘
```

### How It Works

1. The user opens the Streamlit application.
2. The user selects a career preparation feature and provides the required input.
3. For resume-based tasks, the backend extracts text from the uploaded PDF.
4. The application prepares a prompt containing the relevant resume text, job requirements, or interview settings.
5. The backend sends the request to the configured Groq model.
6. The generated response is processed and returned to the frontend.
7. Streamlit presents the analysis, matching insights, interview questions, or feedback.

The exact processing flow depends on the selected feature and the corresponding implementation.

---

## 📂 Project Structure

```text
Blaze - AI Career Assistant/
│
├── app.py                  # Streamlit frontend
├── api.py                  # FastAPI backend
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── .gitignore              # Excluded files and secrets
│
└── src/
    ├── interview.py        # Interview and AI-related logic
    └── pdf_processor.py    # PDF text processing
```

---

## ⚙️ Installation and Setup

### Prerequisites

Install the following before starting:

- Python 3.10 or another version supported by the project dependencies
- Git
- A Groq API account and API key
- A code editor such as Visual Studio Code

### Step 1: Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/adityarao22/Blaze-AI-Career-Assistant.git
cd "Blaze-AI-Career-Assistant"
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```bat
venv\Scripts\activate
```

On macOS or Linux:

```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a file named `.env` in the project root directory.

Add your own Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your actual key locally.

**Security requirements:**

- Never commit `.env` to Git.
- Never place API keys directly in Python source files.
- Never share API keys in screenshots or public issue reports.
- If a key is exposed, revoke it and generate a replacement.

The `.gitignore` file should include:

```gitignore
.env
.env.*
!.env.example
venv/
__pycache__/
*.py[cod]
```

### Step 5: Start the FastAPI Backend

Open the first terminal in the project directory:

```bash
uvicorn api:app --reload
```

The local API server should be available at:

http://127.0.0.1:8000

### Step 6: Open API Documentation

Visit:

http://127.0.0.1:8000/docs

FastAPI provides an interactive documentation page for exploring available endpoints and testing requests.

### Step 7: Start the Streamlit Frontend

Open a second terminal, activate the virtual environment, and run:

```bash
streamlit run app.py
```

Open the local URL shown in the terminal, typically:

http://localhost:8501

Keep the backend running while using the frontend if the application requires API requests.

---

## 🔌 API Overview

Blaze uses FastAPI to expose backend functionality to the frontend.

The precise endpoint names and request formats should be confirmed in `api.py` or the interactive `/docs` page.

| Endpoint / Resource | Purpose |
|---|---|
| `/docs` | Interactive API documentation |
| `/` | Root endpoint, if implemented |
| `/health` | Health check, if implemented |
| Resume analysis endpoint | Resume analysis, if implemented |
| `/match-job` | Job matching, if implemented |
| Interview endpoint | Interview preparation, if implemented |

### Example: Testing Job Matching

If `/match-job` is available, open the Swagger page at `http://127.0.0.1:8000/docs`.

1. Find the `/match-job` endpoint.
2. Expand it.
3. Click **Try it out**.
4. Provide the request body required by the endpoint schema.
5. Click **Execute**.
6. Review the response.

Use the exact request fields shown by Swagger; the schema may change as the project evolves.

---

## 🧪 Testing and Verification

Before using or demonstrating the application, verify the following:

- [ ] Dependencies install successfully.
- [ ] The `.env` file is present locally and is ignored by Git.
- [ ] The backend starts without errors.
- [ ] The `/docs` page loads.
- [ ] The Streamlit frontend starts successfully.
- [ ] Resume analysis works with a suitable text-based PDF.
- [ ] Job matching returns a structured result.
- [ ] Interview preparation generates relevant questions.
- [ ] Mock interview mode follows the expected question-and-answer workflow.
- [ ] API errors are handled appropriately.

These are recommended checks, not a claim that every test has been automated.

---

## 🔐 Security and Privacy

Blaze uses an external AI service to generate responses.

- Store credentials in environment variables.
- Keep `.env` out of version control.
- Never commit real API keys or personal access tokens.
- Avoid uploading sensitive personal information unnecessarily.
- Review the external AI provider's privacy terms before processing confidential resume data.
- Use a fresh API key if the previous one has been exposed.

A `.gitignore` rule prevents future accidental additions but does not remove a secret from earlier Git commits. Exposed credentials must be revoked, and affected Git history must be handled separately.

---

## ⚠️ Limitations

- Generated recommendations may be inaccurate or incomplete.
- Job match scores are estimates rather than objective hiring probabilities.
- AI-generated answers should be verified against reliable learning materials.
- PDF text extraction may perform poorly on scanned or image-only resumes.
- Results depend on the model, prompt, input quality, and service availability.
- The application requires valid API credentials and access to the configured AI service.

---

## 🚀 Future Improvements

Potential enhancements include:

- Resume keyword optimization for applicant tracking systems.
- Support for additional resume formats.
- Downloadable resume analysis reports.
- Improved job-description comparison and skill-gap recommendations.
- Interview scoring with transparent evaluation criteria.
- Persistent practice history and progress tracking.
- Unit tests and automated API integration tests.
- Deployment with secure environment configuration.
- Better handling of rate limits, timeouts, and invalid inputs.
- Accessibility and mobile interface improvements.

These are possible future enhancements and should not be interpreted as existing functionality unless implemented.

---

## 🎯 Project Objective

The objective of Blaze is to bring resume feedback, job matching, and interview preparation into one practical application.

By combining a Python backend, an interactive frontend, and Generative AI, the project demonstrates how AI can support common career preparation tasks.

---

## 👨‍💻 Author

**Aditya Rao**

GitHub: [@adityarao22](https://github.com/adityarao22)

Project: [Blaze — AI Career Assistant](https://github.com/adityarao22/Blaze-AI-Career-Assistant)
