import streamlit as st
import PyPDF2
import docx2txt
import re

st.set_page_config(page_title="AI Resume Screener", layout="centered")
st.title("🧠 AI-Powered Resume Screener")
st.write("Upload your resume and get a predicted job role (supports PDF, DOCX, TXT).")


uploaded_file = st.file_uploader("📄 Upload Resume", type=["pdf", "docx", "txt"])

def extract_text(file):
    if file.name.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file)
        return "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file.name.endswith('.docx'):
        return docx2txt.process(file)
    elif file.name.endswith('.txt'):
        return file.read().decode("utf-8")
    return ""

def predict_category(text):
    text = text.lower()

    categories = {
        "UI/UX Designer": r"\b(ui|ux|figma|sketch|adobe xd|wireframe|prototype)\b",
        "Data Scientist": r"\b(data scientist|machine learning|deep learning|tensorflow|scikit-learn|ml model)\b",
        "Data Analyst": r"\b(data analyst|power bi|tableau|excel|sql|data visualization)\b",
        "Software Developer": r"\b(python developer|software engineer|java|javascript|c\+\+|react|developer)\b",
        "Business Analyst": r"\b(business analyst|requirement gathering|gap analysis|stakeholder|business analysis)\b",
        "Digital Marketer": r"\b(digital marketing|seo|content marketing|social media|adwords)\b",
        "Project Manager": r"\b(project manager|scrum|agile|jira|pmp|project management)\b",
        "DevOps Engineer": r"\b(devops|aws|docker|kubernetes|ci/cd|jenkins)\b",
    }

    for role, pattern in categories.items():
        if re.search(pattern, text):
            return role

    return "Other"


if uploaded_file:
    st.success(f"✅ Uploaded: {uploaded_file.name}")

    if st.button("🔍 Analyze Resume"):
        with st.spinner("Analyzing..."):
            resume_text = extract_text(uploaded_file)

            if resume_text.strip() == "":
                st.warning("⚠️ No readable text found in the file.")
            else:
                predicted_role = predict_category(resume_text)
                st.subheader("🎯 Predicted Job Category:")
                st.success(predicted_role)
