import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing. Add it to your .env file."
    )

client = Groq(api_key=api_key)

def analyze_resume(resume_text: str, job_description: str) -> str:
    prompt = f"""
    You are an AI career and interview assistant.

    Analyze the resume against the job description.

    RESUME:
    {resume_text[:12000]}

    JOB DESCRIPTION:
    {job_description[:6000]}

    Return your analysis with these sections:

    1. Resume Summary
    2. Relevant Skills
    3. Matching Skills
    4. Missing or Underrepresented Skills
    5. Resume-Job Match Estimate (0-100%)
    6. Suggestions for Improvement
    7. Five Relevant Interview Questions

    Base your analysis only on the information provided.
    Do not invent qualifications or experience.
    Explain that the match estimate is an AI-generated estimate,
    not a validated hiring score.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You provide honest, practical career feedback. "
                    "Never invent facts about a candidate."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_tokens=1500,
    )
    return response.choices[0].message.content or ""

import json
def generate_interview_questions(
    role: str,
    interview_type: str,
    difficulty: str,
    num_questions: int,
    resume_text: str = "",
    job_description: str = ""
) -> list:
    """
    Generate interview questions and sample answers
    using the Groq LLM.
    """

    prompt = f"""
You are an experienced technical interviewer and career coach.

Generate exactly {num_questions} interview questions
for the following candidate.

Target role: {role}
Interview type: {interview_type}
Difficulty: {difficulty}

Resume:
{resume_text[:8000] or "No resume provided."}

Job description:
{job_description[:4000] or "No job description provided."}

Instructions:
1. Make questions relevant to the target role.
2. For technical interviews, focus on role-relevant concepts.
3. For HR interviews, focus on communication, motivation,
   strengths, weaknesses, and teamwork.
4. For project interviews, focus on the candidate's projects
   and decisions, using only available project information.
5. Provide a clear, useful sample answer for every question.
6. Do not invent candidate experience or achievements.
7. Adjust question complexity to the selected difficulty.
8. Avoid duplicate questions.

Return valid JSON with this exact structure:
{{
  "questions": [
    {{
      "question": "Interview question",
      "sample_answer": "Example answer",
      "topic": "Topic name"
    }}
  ]
}}

Return JSON only. Do not include Markdown fences.
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful interview coach. "
                    "Generate realistic questions and honest "
                    "sample answers. Follow the requested JSON format."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=3500,
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content or "{}"
    data = json.loads(content)
    questions = data.get("questions", [])

    if not isinstance(questions, list) or not questions:
        raise ValueError("The AI did not generate valid questions.")
    return questions
def match_job(resume_text: str, job_description: str) -> dict:
    """
    Compare a candidate's resume with a specific job description.
    Returns structured job-matching results using Groq.
    """
    if not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    if not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    prompt = f"""
You are an expert resume-to-job matching assistant.

Compare the candidate's resume with the job description.

RESUME:
{resume_text[:12000]}

JOB DESCRIPTION:
{job_description[:6000]}

Return a JSON object with exactly these fields:
{{
  "match_percentage": 75,
  "match_summary": "Brief explanation of the match",
  "matched_skills": ["Python", "SQL"],
  "missing_skills": ["Power BI"],
  "matching_qualifications": ["Qualifications supported by the resume"],
  "qualification_gaps": ["Required qualifications not demonstrated"],
  "strengths": ["Relevant evidence from the resume"],
  "recommendations": ["Specific suggestions for improvement"]
}}

Rules:
1. Match percentage must be a number from 0 to 100.
2. Base the score on demonstrated skills, experience, and qualifications.
3. Do not invent skills, certifications, education, or experience.
4. If information is unavailable, say so rather than assuming.
5. Distinguish missing evidence from proof that a skill is absent.
6. Keep recommendations practical and specific.
7. The score is an AI-generated estimate, not a validated hiring score.
8. Return valid JSON only, without Markdown fences.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an honest job-matching assistant. "
                    "Evaluate only the evidence provided. "
                    "Never fabricate candidate qualifications."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_tokens=1800,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    data = json.loads(content)

    score = data.get("match_percentage")

    if not isinstance(score, (int, float)) or isinstance(score, bool):
        raise ValueError("The AI returned an invalid match percentage.")

    data["match_percentage"] = max(0, min(100, score))

    return data