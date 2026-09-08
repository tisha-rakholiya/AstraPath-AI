import streamlit as st
import requests
import PyPDF2
import io
import re
from io import BytesIO
from reportlab.pdfgen import canvas

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AstraPath AI", page_icon="🚀")

API_KEY = st.secrets["GROQ_API_KEY"]

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ---------------- PDF FUNCTION ----------------
def create_pdf(text):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    y = 800
    p.drawString(50, y, "AstraPath AI Report")

    for line in text.split("\n"):
        y -= 15
        if y < 50:
            p.showPage()
            y = 800
        p.drawString(50, y, line[:100])

    p.save()
    buffer.seek(0)
    return buffer

# ---------------- AI ANALYSIS ----------------
def analyze_resume(resume_text):
    prompt = f"""
Analyze the following resume as an expert Career Advisor specializing in Space, Research, AI, Data Science, and Engineering careers.

Provide your response in the following structured format:

1. ATS Score Analysis
- ATS Score out of 100
- Formatting & Structure: /20
- Technical Skills: /20
- Projects & Practical Experience: /20
- Education & Achievements: /20
- Keywords & Industry Relevance: /20

2. Top 5 Skills Identified

3. Skill Gap Analysis for ISRO, DRDO, Research, AI, and Space Technology Roles
- High Priority Skills
- Medium Priority Skills
- Low Priority Skills

4. Candidate Strengths

5. Areas for Improvement

6. Personalized Career Roadmap
- Next 3 Months
- Next 6 Months
- Next 12 Months

7. Best Career Roles for This Candidate

8. Internship & Opportunity Recommendations

9. Recommended Courses
Provide courses in Markdown format:
[Course Name](Course Link)

Include:
- Platform
- Difficulty Level
- Duration
- Why Recommended

10. Project Recommendations
Include:
- Project Title
- Difficulty
- Technologies
- Expected Outcome

11. Final Recruiter Feedback
- Overall Profile Rating (/10)
- Interview Readiness (/10)
- Research Readiness (/10)
- Industry Readiness (/10)

Resume:
{resume_text}
"""

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    result = response.json()

    if response.status_code != 200:
        return f"⚠️ API Error: {result}"

    if "choices" not in result:
        return "⚠️ Unable to generate analysis right now. Please try again later."

    return result["choices"][0]["message"]["content"]

# ---------------- UI ----------------
st.title("🚀 AstraPath AI")
st.subheader("AI Career Agent for Space & Research Aspirants")
st.markdown("*Built for ISRO | DRDO | NASA dreamers*")

uploaded_file = st.file_uploader(
    "Upload Your Resume (PDF)",
    type="pdf"
)

job_description = st.text_area(
    "Paste Job Description (Optional)"
)

# ---------------- RESUME PROCESSING ----------------
if uploaded_file:

    pdf_reader = PyPDF2.PdfReader(
        io.BytesIO(uploaded_file.read())
    )

    resume_text = ""

    for page in pdf_reader.pages:
        page_text = page.extract_text()

        if page_text:
            resume_text += page_text

    st.success("✅ Resume uploaded successfully!")

    # JD Match
    if job_description:

        resume_words = set(resume_text.lower().split())
        jd_words = set(job_description.lower().split())

        match_percent = int(
            len(resume_words & jd_words)
            / max(len(jd_words), 1)
            * 100
        )

        st.subheader("🎯 Resume Match Score")
        st.progress(match_percent / 100)
        st.write(f"{match_percent}% Match")

    # AI Analysis
    if st.button("🚀 Analyze My Career Path"):

        with st.spinner(
            "AstraPath AI is analyzing your resume..."
        ):
            analysis = analyze_resume(resume_text)

        # ATS Score Extraction
        match = re.search(
            r'ATS Score.*?(\d+)',
            analysis,
            re.IGNORECASE
        )

        if match:
            score = int(match.group(1))

            st.subheader("📊 ATS Score")
            st.progress(score / 100)
            st.success(f"{score}/100")

        st.markdown("## 📊 Your Career Analysis")
        st.markdown(analysis)

        # PDF Download
        pdf = create_pdf(analysis)

        st.download_button(
            "📄 Download PDF Report",
            data=pdf,
            file_name="AstraPath_Report.pdf",
            mime="application/pdf"
        )

        st.balloons()
