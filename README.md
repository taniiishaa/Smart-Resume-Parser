# 🤖 Smart Resume Analyzer & ATS Scorer

## ✨ Project Summary: Data-Driven Candidate Screening

This application transforms the slow, subjective resume review process into a fast, objective, and data-driven assessment. Built on modern NLP techniques (spaCy) and the Streamlit framework, it acts as a lightweight Applicant Tracking System (ATS) tool, providing an immediate, quantified match score for any candidate against specific job requirements.

## 🚀 Key Features & Value Proposition

| Feature | Business Impact & Professional Rationale |
| :--- | :--- |
| **Weighted ATS Score** | Generates a **Final Match Score** by combining **Skill Alignment (60%)** and **Estimated Years of Experience (YoE) (40%)**. This transparent, weighted metric ensures candidates are evaluated on criteria critical to the role. |
| **Universal Parsing Engine** | Extracts Name, Contact Info, Education, and Experience from **PDF** and **DOCX** documents. Designed to analyze resumes for **any professional role**. |
| **One-Click Data Export** | Facilitates seamless data workflow by allowing users to **download the full analysis as a JSON file**. |
| **Visual Alignment Dashboard** | Provides an immediate, clear **bar chart visualization** of required JD keywords versus found skills. |

***

## 🧠 Architectural Deep Dive: How the Parser Works

The system operates in a four-stage pipeline to convert unstructured documents into actionable data:

### Stage 1: Document Ingestion and Preprocessing
1.  **Text Extraction:** Specialized libraries (`pdfminer.six`, `docx2txt`) are used to reliably extract the raw text content from the PDF/DOCX files.
2.  **Cleaning:** The raw text is stripped of excessive noise (newlines, tabs) for accurate NLP processing.

### Stage 2: Information Extraction (NLP & RegEx)
1.  **Name/Contact/Education:** Regular Expressions (RegEx) are used for structured data like Email, Phone, and Degree Qualifications.
2.  **Skill Detection:** **spaCy's PhraseMatcher** efficiently scans the text against a list of known technical keywords.
3.  **YoE Calculation:** Date RegEx patterns are applied to find all experience ranges, and the total duration is calculated in years.

### Stage 3: Scoring and Comparison
1.  **Keyword Matching:** The extracted skills are compared against the skills found in the Job Description (JD).
2.  **Final Score Calculation:** The ATS score is computed using the weighted formula:
    $$
    \text{Score} = (0.60 \times \text{Skill Match } \%) + (0.40 \times \text{YoE Score})
    $$

### Stage 4: Visualization and Reporting
1.  **Data Visualization:** Results are rendered in a professional Streamlit UI, featuring key metrics and a custom **Matplotlib Bar Chart** for visual comparison.
2.  **Export:** All final data and metrics are packaged into a JSON file, ready for download and integration.

***

## ⚙️ How to Run Locally

### Prerequisites

You need **Python 3.8+** installed and the dependencies listed in `requirements.txt`.

### Step 1: Clone the Repository

```bash
git clone https://github.com/taniiishaa/Smart-Resume-Parser
cd Smart-Resume-Parser
