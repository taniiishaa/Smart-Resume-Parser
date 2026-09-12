# 📄 Smart Resume Analyzer

### Turn an unstructured resume into structured candidate insights.

Recruiters don't receive resumes as clean datasets.

They receive **PDFs, DOCX files, different layouts, inconsistent formatting, skill lists, experience ranges, and hundreds of lines of text**.

This project explores how lightweight NLP and rule-based extraction can transform that messy information into something much easier to analyze.

> **Upload a resume → provide a Job Description → extract → compare → score → export.**

---

## ✦ The Idea

Think of a resume as an unstructured document sitting on one side...

```text
┌───────────────────────────┐
│       RESUME FILE         │
│                           │
│  Name                     │
│  Contact                  │
│  Education                │
│  Experience               │
│  Skills                   │
│  Projects                 │
└─────────────┬─────────────┘
              │
              ▼
       DOCUMENT PARSER
              │
              ▼
┌───────────────────────────┐
│    STRUCTURED PROFILE     │
│                           │
│  Candidate                │
│  Contact                  │
│  Skills                   │
│  Education                │
│  Experience               │
└─────────────┬─────────────┘
              │
              ▼
       JOB DESCRIPTION
              │
              ▼
       SKILL COMPARISON
              │
              ▼
        MATCH SCORE
```

The result isn't meant to replace human recruitment decisions.

Instead, it provides a **transparent first-pass analysis** of how closely a resume aligns with a supplied Job Description.

---

# 🧩 What Happens Inside?

The application combines several small techniques rather than relying on one large AI model.

### 01 — Document Extraction

Supports:

* 📕 PDF
* 📘 DOCX

PDF text is extracted with `pdfminer.six`, while DOCX content is processed with `docx2txt`.

The extracted document is then normalized before NLP processing.

---

### 02 — Candidate Information Extraction

The parser attempts to identify:

| Information   | Technique                            |
| ------------- | ------------------------------------ |
| 👤 Name       | spaCy NER + fallback logic           |
| 📧 Email      | Regular Expression                   |
| 📞 Phone      | Regular Expression                   |
| 🎓 Education  | Regex-based degree detection         |
| 🛠️ Skills    | spaCy PhraseMatcher                  |
| 💼 Experience | Date-range extraction + date parsing |

This converts a document into a structured candidate profile.

---

# 🧠 Skill Intelligence

The application maintains a configurable list of commonly encountered technical skills.

Examples include:

```text
Python       SQL          Data Analysis
Machine Learning          Deep Learning
NLP          Streamlit    Pandas
NumPy        Docker       Kubernetes
AWS          FastAPI      Flask
React        TensorFlow   Scikit-learn
Matplotlib   Seaborn      Git
```

The same matching mechanism is used on both:

**Resume ↔ Job Description**

That makes it possible to identify the overlap between what a role asks for and what a candidate mentions.

---

## 🔎 From JD to Skill Gap

Suppose the Job Description requires:

```text
Python
SQL
AWS
Docker
FastAPI
```

and the resume contains:

```text
Python
SQL
AWS
Git
Flask
```

The analyzer can conceptually represent the result as:

```text
JOB DESCRIPTION
      │
      ├── Python ──────── ✓ MATCH
      ├── SQL ─────────── ✓ MATCH
      ├── AWS ─────────── ✓ MATCH
      ├── Docker ──────── ✕ MISSING
      └── FastAPI ─────── ✕ MISSING

              ↓

       SKILL ALIGNMENT
```

The interface also visualizes the comparison using a bar chart showing:

* Required JD skills
* Skills found in the resume
* Matched skills

---

# 🎯 The Match Score

The project uses a deliberately simple weighted scoring model.

### Skill Alignment — 60%

The percentage of detected JD skills that are also found in the resume.

### Experience — 40%

Estimated experience is compared against a default requirement of **3 years**, with the contribution capped at that requirement.

The final calculation is:

$$
Score =
0.60(Skill\ Match\ \%)
+
0.40(YoE\ Score)
$$

with the final score capped at **100%**.

### Why this approach?

Because a screening score should be **explainable**.

Instead of producing an unexplained prediction, the application can show:

```text
              FINAL MATCH
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   60% Skills          40% Experience
        │                   │
        ▼                   ▼
   JD Alignment        Estimated YoE
        │                   │
        └─────────┬─────────┘
                  ▼
            Overall Score
```

---

# 🖥️ Inside the Streamlit Interface

The application follows a simple two-sided workflow:

```text
┌──────────────────────┐      ┌──────────────────────────┐
│   INPUT              │      │   ANALYSIS               │
│                      │      │                          │
│ Resume Upload        │ ───► │ Final Match Score        │
│ Job Description      │      │ Experience               │
│                      │      │ Skill Match %             │
│                      │      │ Candidate Details         │
│                      │      │ Skill Visualization       │
└──────────────────────┘      │ Missing / Matched Skills │
                              │ JSON Export               │
                              └──────────────────────────┘
```

The UI provides:

* 🎯 Final Match Score
* 💼 Estimated Years of Experience
* 🌟 Skill Match Percentage
* 👤 Candidate information
* 📊 Skill alignment chart
* 🎓 Education detected
* ✅ Matched skills
* ❌ Missing JD skills
* 📝 Extracted resume text snippet
* 📥 JSON analysis download

---

# 📦 Structured JSON Export

The analysis can be downloaded as a JSON file containing fields such as:

```json
{
    "Score_Final_Match_Percent": 60.0,
    "Score_Skill_Match_Percent": 100.0,
    "YoE_Total_Years": 0.0,
    "Candidate_Name": "Candidate",
    "Candidate_Email": "candidate@example.com",
    "Candidate_Phone": "XXXXXXXXXX",
    "Skills_Matched": [
        "Python",
        "SQL",
        "AWS"
    ],
    "Education_Details": [
        "B.Tech"
    ]
}
```

This makes the output easier to reuse in another application or processing pipeline.

---

# 🧪 A Small Testing Ground

One of the stronger parts of this repository is that it doesn't contain only the application.

It also includes test resumes representing different document scenarios:

```text
test_data/
│
├── test_resume_clean.docx
├── test_resume_clean.pdf
├── test_resume_complex.pdf
├── test_resume_junior.pdf
└── test_resume_senior.pdf
```

Corresponding expected JSON outputs are stored separately:

```text
expected_output/
│
├── test_resume_clean_docx.json
├── test_resume_clean_pdf.json
├── test_resume_complex.json
├── test_resume_junior.json
└── test_resume_senior.json
```

This creates a simple benchmark for checking how the parser behaves across different resumes.

---

# 🛠️ Technology Behind the Project

```text
                 SMART RESUME ANALYZER
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
   STREAMLIT           spaCy             REGEX
       │                 │                 │
       │             NLP / Skills      Contact /
       │              Matching         Education
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
                 DATE EXTRACTION
                         │
                         ▼
                  MATCH SCORING
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
       Visualization             JSON Export
```

### Stack

* **Python**
* **Streamlit**
* **spaCy**
* **spaCy PhraseMatcher**
* **RegEx**
* **dateparser**
* **pdfminer.six**
* **docx2txt**
* **Pandas**
* **NumPy**
* **Matplotlib**

---

# 🚀 Run It Locally

## 1. Clone

```bash
git clone https://github.com/taniiishaa/smart-resume-analyzer.git
cd smart-resume-analyzer
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Download the spaCy model

This project specifically requires the small English spaCy model:

```bash
python -m spacy download en_core_web_sm
```

## 4. Start Streamlit

```bash
streamlit run app.py
```

The application will open in your browser.

---

# 📁 Repository Structure

```text
smart-resume-analyzer/
│
├── app.py
├── requirements.txt
│
├── test_data/
│   ├── test_resume_clean.docx
│   ├── test_resume_clean.pdf
│   ├── test_resume_complex.pdf
│   ├── test_resume_junior.pdf
│   └── test_resume_senior.pdf
│
├── expected_output/
│   ├── test_resume_clean_docx.json
│   ├── test_resume_clean_pdf.json
│   ├── test_resume_complex.json
│   ├── test_resume_junior.json
│   └── test_resume_senior.json
│
└── README.md
```

---

# ⚠️ Know the Boundaries

This project intentionally uses a **lightweight, deterministic approach**.

It is **not a production ATS** and it does not use embeddings, an LLM, or semantic similarity.

Some important limitations include:

* Skills are detected from a predefined skills list.
* Skill matching is keyword/phrase based.
* Experience is estimated from detected date ranges.
* Resume formatting can affect extraction quality.
* Name extraction can require fallback handling.
* The default experience requirement is 3 years.
* The score should be treated as an analytical indicator, not a hiring decision.
* Different wording for the same skill may not always be recognized.

Being explicit about these limitations makes the project more technically credible.

---

# 🌱 Where It Could Go Next

The current rule-based foundation could evolve into a much more capable **Resume Intelligence Platform**.

### Possible upgrades

**Semantic Matching**

Replace exact skill matching with embeddings to understand relationships between terms such as:

```text
"REST API development"
        ↕
"FastAPI / Flask"
```

**LLM-powered extraction**

Use an LLM to identify:

* Job titles
* Companies
* Projects
* Responsibilities
* Technologies
* Achievements

**Batch Resume Screening**

```text
100 Resumes
     │
     ▼
Parallel Parsing
     │
     ▼
JD Matching
     │
     ▼
Candidate Ranking
     │
     ▼
CSV / Database
```

**Recruiter Dashboard**

Add filtering by:

* Match score
* Experience
* Skills
* Education
* Missing requirements

**Database Integration**

Store structured candidate profiles using PostgreSQL or another database.

**API Layer**

Expose the parsing engine through FastAPI for integration with external recruitment systems.

---

# 💭 What This Project Demonstrates

This project isn't just about parsing resumes.

It demonstrates how an unstructured real-world document can move through a complete data-processing pipeline:

```text
UNSTRUCTURED
     │
     ▼
  DOCUMENT
     │
     ▼
   TEXT
     │
     ▼
EXTRACTION
     │
     ▼
STRUCTURED DATA
     │
     ▼
COMPARISON
     │
     ▼
INSIGHT
     │
     ▼
DECISION SUPPORT
```

And that's the part that makes this project valuable.

---

## ✨ Final Thought

> **A resume is written for humans.
> This project teaches software how to read between its lines.**

Built with Python, NLP, document processing, and a little bit of structured logic — turning resumes from documents into data-driven candidate insights.
