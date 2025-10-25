import streamlit as st
import spacy
import re
import os
import json # New import for JSON export
import pandas as pd # New import for potential CSV export (though we use JSON here)
from datetime import datetime
from dateparser import parse as date_parse
from pdfminer.high_level import extract_text
import docx2txt
from spacy.matcher import PhraseMatcher
import matplotlib.pyplot as plt
import numpy as np

# --- Configuration & Initialization ---
# Load the small English spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    st.error("Error loading spaCy model. Run: python -m spacy download en_core_web_sm")
    st.stop()

# Define RegEx Patterns for Contact Info, Dates, and Education
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_REGEX = r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{2,}\s?\d{10})'
DATE_REGEX = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December|\d{1,4})[\s,\-]*(\d{4})?\s*[-–]\s*(present|current|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December|\d{1,4})[\s,\-]*(\d{4})?'
EDUCATION_REGEX = r'(B\.E\.|B\.Tech|M\.Tech|M\.S\.|Ph\.D|BSc|MSc|MBA|BBA|BCA|MCA|Bachelor\s*of\s*Science|Master\s*of\s*Science|Doctorate|Bachelors|Masters|Degree|Diploma)'

# List of common skills (EXPAND THIS LIST!)
SKILLS_LIST = [
    'Python', 'SQL', 'Data Analysis', 'Machine Learning', 'Deep Learning', 
    'NLP', 'Streamlit', 'Pandas', 'NumPy', 'Docker', 'Kubernetes', 'AWS', 
    'JavaScript', 'HTML', 'CSS', 'FastAPI', 'Flask', 'React', 
    'TensorFlow', 'Scikit-learn', 'Matplotlib', 'Seaborn', 'Git'
]

# List of common false positives for name extraction
NAME_FALSE_POSITIVES = {
    'PANDAS', 'PYTHON', 'RESUME', 'CV', 'APPLICATIONS', 'EXPERIENCE', 
    'SKILLS', 'EDUCATION', 'PROFILE', 'CONTACT', 'SUMMARY'
}

# --- Core Information Extraction Functions (UNCHANGED) ---

def extract_text_from_pdf(pdf_file_path):
    try:
        with open(pdf_file_path, 'rb') as file:
            return extract_text(file)
    except Exception as e:
        return f"Error extracting PDF text: {e}"

def extract_text_from_docx(docx_file_path):
    try:
        text = docx2txt.process(docx_file_path)
        return text if text else None
    except Exception as e:
        return f"Error extracting DOCX text: {e}"

def extract_name(nlp_doc):
    for ent in nlp_doc.ents:
        if ent.label_ == 'PERSON':
            name = ent.text.strip()
            if len(name.split()) >= 2 and name.upper() not in NAME_FALSE_POSITIVES:
                return name
            if len(nlp_doc.text.split('\n')) > 0:
                first_line = nlp_doc.text.split('\n')[0].strip()
                if len(first_line.split()) > 1 and len(first_line) > 5:
                    return first_line.split('\n')[0].split('(')[0].strip()
    return "Candidate Name N/A (Review Raw Text)"

def extract_contact_info(raw_text):
    email = re.search(EMAIL_REGEX, raw_text)
    phone = re.search(PHONE_REGEX, raw_text)
    return {
        "Email": email.group(0) if email else "N/A",
        "Phone": phone.group(0) if phone else "N/A"
    }

def extract_skills(nlp_doc, skills_list):
    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp.make_doc(skill) for skill in skills_list]
    matcher.add("SKILL_LIST", patterns)
    matches = matcher(nlp_doc)
    extracted_skills = set()
    for _, start, end in matches:
        span = nlp_doc[start:end]
        extracted_skills.add(span.text)
    return list(extracted_skills)

def calculate_yoe(raw_text):
    total_yoe = 0.0
    today = datetime.now()
    date_ranges = re.findall(DATE_REGEX, raw_text, re.IGNORECASE)
    if not date_ranges: return 0.0
    job_durations = []
    for date_tuple in date_ranges:
        date_str = ' '.join(filter(None, date_tuple)).strip()
        if ' - ' in date_str: parts = date_str.split(' - ', 1)
        elif '–' in date_str: parts = date_str.split('–', 1)
        else: continue
        if len(parts) != 2: continue
        start_date_str, end_date_str = parts
        start_date = date_parse(start_date_str, settings={'PREFER_DAY_OF_MONTH': 'last', 'PREFER_LOCALE_DATE_ORDER': False})
        if 'present' in end_date_str.lower() or 'current' in end_date_str.lower(): end_date = today
        else: end_date = date_parse(end_date_str, settings={'PREFER_DAY_OF_MONTH': 'last', 'PREFER_LOCALE_DATE_ORDER': False})
        if start_date and end_date and start_date < end_date:
            duration = end_date - start_date
            years = duration.days / 365.25
            job_durations.append(years)
    total_yoe = sum(job_durations)
    return total_yoe
    
def extract_education(raw_text):
    extracted_education = set()
    text_upper = raw_text.upper()
    education_keywords = ['EDUCATION', 'ACADEMICS', 'QUALIFICATIONS']
    start_index = -1
    for keyword in education_keywords:
        if keyword in text_upper:
            start_index = text_upper.find(keyword)
            break
    if start_index == -1: return ["N/A"]
    education_section = raw_text[start_index:] 
    matches = re.findall(EDUCATION_REGEX, education_section, re.IGNORECASE)
    for match in matches:
        if len(match.strip()) > 3: extracted_education.add(match.strip())
    return list(extracted_education)

def calculate_final_score(skill_match_percent, total_yoe, jd_yoe_requirement=3):
    skill_score_component = 0.6 * skill_match_percent 
    experience_cap = float(jd_yoe_requirement)
    yoe_multiplier = min(total_yoe, experience_cap) / experience_cap
    yoe_score_component = 0.4 * (yoe_multiplier * 100)
    final_score = skill_score_component + yoe_score_component
    return min(final_score, 100.0)

def create_skill_bar_chart(jd_skills_set, resume_skills_set, matched_skills):
    data = {
        'Required (JD)': len(jd_skills_set),
        'Found (Resume)': len(resume_skills_set),
        'Matched': len(matched_skills)
    }
    categories = list(data.keys())
    values = list(data.values())
    colors = ['#4F8BF9', '#7DD97D', '#FF6347']
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(categories, values, color=colors)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval), 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_ylabel('Skill Count', fontsize=10)
    ax.set_title('Skill Comparison: Resume vs. Job Description', fontsize=12, fontweight='bold')
    ax.set_ylim(0, max(values) * 1.2 if values else 10)
    plt.tight_layout()
    return fig

def parse_resume(raw_text, skills_list):
    clean_text = raw_text.replace('\n', ' ').replace('\t', ' ')
    doc = nlp(clean_text)
    contact_info = extract_contact_info(clean_text)
    name = extract_name(doc)
    skills = extract_skills(doc, skills_list)
    total_experience = calculate_yoe(clean_text)
    education = extract_education(clean_text)
    
    return {
        "Name": name,
        "Email": contact_info["Email"],
        "Phone": contact_info["Phone"],
        "Skills Found": skills,
        "Total Experience (Years)": f"{total_experience:.1f}", 
        "Education": education,
        "Raw Text Snippet": clean_text
    }

# --- NEW EXPORT FUNCTION ---

def export_data_to_json(parsed_data, final_score, skill_match_percent, total_yoe, filename="candidate_analysis"):
    """Adds final metrics to parsed data and converts it to a JSON string."""
    
    # Create a cleaner dictionary for export
    export_dict = {
        "Score_Final_Match_Percent": round(final_score, 2),
        "Score_Skill_Match_Percent": round(skill_match_percent, 2),
        "YoE_Total_Years": round(total_yoe, 1),
        "Candidate_Name": parsed_data.get("Name", "N/A"),
        "Candidate_Email": parsed_data.get("Email", "N/A"),
        "Candidate_Phone": parsed_data.get("Phone", "N/A"),
        "Skills_Matched": parsed_data.get("Skills Found", []),
        "Education_Details": parsed_data.get("Education", []),
    }
    
    # Format the file name
    file_name = f"{filename}_{export_dict['Candidate_Name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json"
    
    return json.dumps(export_dict, indent=4), file_name

# --- Streamlit UI (The Frontend - MODIFIED) ---

def main():
    st.set_page_config(page_title="Smart Resume Parser", layout="wide")
    
    # Custom Header
    st.markdown("""
        <div style='background-color:#007bff; padding:15px; border-radius:10px; text-align:center;'>
            <h1 style='color:white; margin:0;'>
                🤖 Smart Resume Analyzer & ATS Scorer
            </h1>
            <p style='color:#e0e0e0; margin:5px 0 0;'>
                Automated Candidate Screening for All Professional Roles
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

    col_input, col_output = st.columns([1, 1.5])

    with col_input:
        st.subheader("1. Job Requirements & Resume")
        
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF/DOCX) 📄", 
            type=["pdf", "docx"]
        )
        
        job_description = st.text_area(
            "Paste Job Description Text 📋",
            height=300
        )
        
        jd_skills = extract_skills(nlp(job_description), SKILLS_LIST)
        jd_skills_set = set(jd_skills)
        st.success(f"**JD Keywords Detected ({len(jd_skills)}):** {', '.join(jd_skills) if jd_skills else 'None'}")


    if uploaded_file and job_description:
        # --- File Handling and Parsing ---
        with st.status("Analyzing Resume... Please wait.", expanded=True) as status:
            st.write("Extracting Text from Document...")
            file_extension = uploaded_file.name.split('.')[-1].lower()
            temp_file_path = f"temp_resume.{file_extension}"
            raw_text = ""
            
            try:
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                if file_extension == 'pdf':
                    raw_text = extract_text_from_pdf(temp_file_path)
                elif file_extension == 'docx':
                    raw_text = extract_text_from_docx(temp_file_path)
                
            except Exception as e:
                st.error(f"File processing error: {e}")
                status.update(label="Analysis Failed", state="error", expanded=False)
                return
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

            if not raw_text:
                status.update(label="Analysis Failed: Could not extract text.", state="error", expanded=False)
                return
                
            st.write("Running NLP & Feature Extraction...")
            parsed_data = parse_resume(raw_text, SKILLS_LIST)
            total_yoe = float(parsed_data["Total Experience (Years)"])
            resume_skills = set(parsed_data["Skills Found"])
            
            st.write("Calculating Match Score...")
            matched_skills = resume_skills.intersection(jd_skills_set)
            
            if jd_skills_set:
                skill_match_percent = (len(matched_skills) / len(jd_skills_set)) * 100
            else:
                skill_match_percent = 0.0

            final_score = calculate_final_score(skill_match_percent, total_yoe)
            
            # Prepare export data
            json_data, filename = export_data_to_json(parsed_data, final_score, skill_match_percent, total_yoe)

            status.update(label="✅ Analysis Complete!", state="complete", expanded=False)

        # --- Display Results ---
        with col_output:
            st.subheader("2. Candidate Assessment")
            
            # --- Overall Score Card ---
            score_col1, score_col2, score_col3 = st.columns(3)

            with score_col1:
                st.markdown(f"""
                    <div style='border: 2px solid #007bff; border-radius: 10px; padding: 10px; text-align: center; background-color: #e6f0ff;'>
                        <p style='font-size:14px; margin:0; color:#007bff;'>🎯 **FINAL ATS SCORE**</p>
                        <h2 style='font-size:40px; margin:0; color:#007bff;'>{final_score:.1f}%</h2>
                    </div>
                    """, unsafe_allow_html=True)

            with score_col2:
                st.metric(label="💼 Total YoE (Estimated)", value=f"{total_yoe:.1f} Yrs")

            with score_col3:
                st.metric(label="🌟 Skill Match %", value=f"{skill_match_percent:.1f}%")
                
            # --- NEW: Download Button ---
            st.download_button(
                label="⬇️ Download Analysis (JSON)",
                data=json_data,
                file_name=filename,
                mime="application/json",
                help="Download the complete parsed data and final scores."
            )
            
            st.markdown("---")
            
            # --- Candidate Details ---
            st.markdown(f"**👤 Candidate:** **{parsed_data['Name']}**")
            st.markdown(f"**📧 Contact:** `{parsed_data['Email']}` | **📞 Phone:** `{parsed_data['Phone']}`")
            
            with st.expander("📝 View Resume Summary/Objective (Unstructured Text)"):
                st.text_area(
                    label="Resume Snippet", 
                    value=parsed_data['Raw Text Snippet'][:600] + "..." if len(parsed_data['Raw Text Snippet']) > 600 else parsed_data['Raw Text Snippet'], 
                    height=200, 
                    disabled=True,
                    label_visibility="collapsed"
                )
            
            st.subheader("📊 Skill Alignment Visual")
            fig = create_skill_bar_chart(jd_skills_set, resume_skills, matched_skills)
            st.pyplot(fig)
            
            st.markdown("---")

            # --- Detailed Breakdown ---
            st.subheader("🔍 Key Insights")
            
            st.info(f"🎓 **Education Found:** {', '.join(parsed_data['Education'])}")

            st.success(f"✅ **Matched Skills ({len(matched_skills)}):** {', '.join(matched_skills)}")
            
            missing_skills = jd_skills_set - resume_skills
            st.error(f"❌ **Missing JD Skills ({len(missing_skills)}):** {', '.join(missing_skills)}")
            
            with st.expander("Show All Parsed Data (JSON)"):
                 st.json(parsed_data)

    elif uploaded_file:
        st.warning("Please paste a Job Description in the text box to start the analysis.")
        
    elif job_description:
        st.warning("Please upload a Resume to start the analysis.")


if __name__ == '__main__':
    main()