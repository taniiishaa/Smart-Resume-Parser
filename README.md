# 🤖 Smart Resume Analyzer & ATS Scorer

## ✨ Project Summary: Data-Driven Candidate Screening

This application transforms the slow, subjective resume review process into a fast, objective, and data-driven assessment. Built on modern NLP techniques (spaCy) and the Streamlit framework, it acts as a lightweight Applicant Tracking System (ATS) tool, providing an immediate, quantified **Final Match Score** for any candidate against specific job requirements.

## 🚀 Key Features & Value Proposition

| Feature | Professional Rationale & Business Impact |
| :--- | :--- |
| **Weighted ATS Score** | Generates a Final Score by combining **Skill Alignment (60%)** and **Estimated Years of Experience (YoE) (40%)**. This provides an objective, transparent, and defensible screening metric. |
| **Universal Parsing Engine** | Extracts detailed data (Name, Contact, Education, YoE, Skills) from **PDF** and **DOCX** files, supporting a universal document pipeline for various roles . |
| **One-Click Data Export** | Facilitates seamless integration into HR workflows by providing a **JSON export** of all parsed data and scores. |
| **Visual Alignment Dashboard** | Provides an immediate **Bar Chart Visualization** comparing required JD keywords versus found skills, instantly highlighting skill gaps. |

***

## 🧠 Architectural Deep Dive: How the Parser Works

The system operates in a multi-stage pipeline to convert unstructured documents into actionable data:

### Stage 1: Document Ingestion and Text Preprocessing
1.  **Extraction:** Leverages specialized Python libraries (`pdfminer.six`, `docx2txt`) to reliably extract raw text content from binary file formats.
2.  **Cleaning:** The raw text is stripped of noise (newlines, tabs) and normalized for highly accurate NLP processing.

### Stage 2: Information Extraction (NLP & RegEx)
1.  **Structured Data:** Regular Expressions (RegEx) are used for highly accurate extraction of Email, Phone, and formalized Degree Qualifications.
2.  **Semantic Data (Skills/YoE):** **spaCy's PhraseMatcher** rapidly detects skills against a defined list, while robust date RegEx patterns calculate total **Years of Experience** from all found date ranges.

### Stage 3: Scoring and Comparison
1.  **Keyword Matching:** Extracted candidate skills are precisely intersected with the skills required by the Job Description (JD).
2.  **Weighted Score:** The final ATS Score is computed using the weighted formula, reflecting the relative importance of skills versus experience:
    $$
    \text{Score} = (0.60 \times \text{Skill Match } \%) + (0.40 \times \text{YoE Score})
    $$

***

## ⚙️ How to Run Locally

### Prerequisites

Ensure you have **Python 3.8+** installed on your system.

### Step 1: Clone the Repository

```bash
git clone https://github.com/taniiishaa/Smart-Resume-Parser
cd Smart-Resume-Parser
