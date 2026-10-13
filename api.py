from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

from src.pdf_processor import extract_resume_text
from src.interview import analyze_resume, generate_interview_questions
from src.interview import match_job


app = FastAPI(
    title="Blaze - AI Career Assistant",
    description="AI-powered Resume Analysis, Job Matching, and Interview Preparation",
    version="1.0.0",
)


# ---------------- REQUEST MODELS ----------------

class ResumeAnalysisRequest(BaseModel):
    resume_text: str = Field(min_length=1, max_length=12000)
    job_description: str = Field(min_length=1, max_length=6000)


class InterviewRequest(BaseModel):
    role: str = Field(min_length=1, max_length=150)
    interview_type: str = Field(min_length=1, max_length=50)
    difficulty: str = Field(min_length=1, max_length=30)
    num_questions: int = Field(default=5, ge=1, le=10)
    resume_text: str = Field(default="", max_length=8000)
    job_description: str = Field(default="", max_length=4000)


class JobMatchRequest(BaseModel):
    resume_text: str = Field(min_length=1, max_length=12000)
    job_description: str = Field(min_length=1, max_length=6000)



# ---------------- HOME AND HEALTH ----------------

@app.get("/")
def home():
    return {
        "success": True,
        "message": "Blaze AI API is running!",
    }


@app.get("/health")
def health_check():
    return {"success": True, "status": "healthy"}


# ---------------- RESUME UPLOAD ----------------

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF resume.",
        )

    try:
        pdf_bytes = await file.read()

        if not pdf_bytes:
            raise HTTPException(
                status_code=400,
                detail="The uploaded PDF is empty.",
            )

        resume_text = extract_resume_text(pdf_bytes)

        if not resume_text or not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the PDF.",
            )

        return {
            "success": True,
            "filename": file.filename,
            "text": resume_text,
            "message": "Resume uploaded successfully.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        print(f"PDF processing error: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=400,
            detail="Unable to process this PDF.",
        )
    finally:
        await file.close()


# ---------------- RESUME ANALYSIS ----------------

@app.post("/analyze-resume")
def analyze_resume_endpoint(request: ResumeAnalysisRequest):
    try:
        result = analyze_resume(
            request.resume_text,
            request.job_description,
        )
        return {"success": True, "analysis": result}

    except Exception as exc:
        print(f"Resume analysis error: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Resume analysis failed. Please try again.",
        )


# ---------------- INTERVIEW GENERATION ----------------

@app.post("/generate-interview")
def generate_interview_endpoint(request: InterviewRequest):
    allowed_types = {"HR", "Technical", "Project-Based", "Mixed"}
    allowed_difficulties = {"Beginner", "Intermediate", "Advanced"}

    if request.interview_type not in allowed_types:
        raise HTTPException(
            status_code=422,
            detail="Invalid interview type.",
        )

    if request.difficulty not in allowed_difficulties:
        raise HTTPException(
            status_code=422,
            detail="Invalid difficulty level.",
        )

    try:
        questions = generate_interview_questions(
            role=request.role.strip(),
            interview_type=request.interview_type,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
            resume_text=request.resume_text,
            job_description=request.job_description,
        )

        return {
            "success": True,
            "role": request.role.strip(),
            "interview_type": request.interview_type,
            "difficulty": request.difficulty,
            "questions": questions,
        }

    except Exception as exc:
        print(f"Interview generation error: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Interview generation failed. Check the API terminal.",
        )


# ---------------- JOB MATCHING ----------------

@app.post("/match-job")
def match_job_endpoint(request: JobMatchRequest):
    try:
        result = match_job(
            resume_text=request.resume_text,
            job_description=request.job_description,
        )

        return {
            "success": True,
            "analysis": result,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e),
        )

    except Exception as e:
        print(
            f"Job matching error: {type(e).__name__}: {e}"
        )
        raise HTTPException(
            status_code=502,
            detail="Job matching failed. Please try again.",
        )