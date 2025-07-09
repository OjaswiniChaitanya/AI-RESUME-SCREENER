import streamlit as st
import PyPDF2
import docx2txt
import re
import pandas as pd
from io import StringIO

# ------------------------------
# Page Setup
# ------------------------------
st.set_page_config(page_title="AI Resume Screener", layout="wide")
st.title("🧠 AI-Powered Resume Screener")
st.write("Upload one or more resumes and get predicted job roles (supports PDF, DOCX, TXT).")

uploaded_files = st.file_uploader("📄 Upload Resume(s)", type=["pdf", "docx", "txt"], accept_multiple_files=True)

# ------------------------------
# Job Role Categories
# ------------------------------
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

# ------------------------------
# Helper Functions
# ------------------------------
def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        return "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file.name.endswith(".docx"):
        return docx2txt.process(file)
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    return ""

def predict_roles(text):
    text = text.lower()
    role_scores = {}
    for role, pattern in categories.items():
        matches = re.findall(pattern, text)
        if matches:
            role_scores[role] = len(matches)
    return dict(sorted(role_scores.items(), key=lambda item: item[1], reverse=True))

def create_csv(results):
    rows = []
    for result in results:
        filename = result["filename"]
        for role, score in result["matched_roles"].items():
            rows.append({"Filename": filename, "Role": role, "Keyword Matches": score})
    return pd.DataFrame(rows)

# ------------------------------
# Resume Analysis Logic
# ------------------------------
if uploaded_files:
    st.success(f"✅ Uploaded {len(uploaded_files)} file(s).")

    if st.button("🔍 Analyze Resumes"):
        results = []

        for file in uploaded_files:
            st.markdown("---")
            st.subheader(f"📄 {file.name}")

            with st.spinner("Analyzing..."):
                text = extract_text(file)

                if not text.strip():
                    st.warning("⚠ No readable text found in this file.")
                    continue

                matched_roles = predict_roles(text)

                if not matched_roles:
                    st.info("🤔 No specific job role matched.")
                else:
                    top_role = next(iter(matched_roles))
                    st.success(f"🎯 *Best Match*: {top_role} ({matched_roles[top_role]} keyword matches)")
                    st.write("📌 Other Matches:")
                    for role, count in list(matched_roles.items())[1:]:
                        st.write(f"- {role}: {count} keyword match{'es' if count > 1 else ''}")

                with st.expander("📃 View Extracted Resume Text"):
                    st.text_area("Resume Content", text, height=300)

                results.append({
                    "filename": file.name,
                    "matched_roles": matched_roles
                })

        # --- CSV Download ---
        if results:
            df = create_csv(results)
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download CSV Results",
                data=csv_buffer.getvalue(),
                file_name="resume_predictions.csv",
                mime="text/csv"
            )
