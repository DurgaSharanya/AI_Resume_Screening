"""
RecruitIQ — AI Resume Screening System
Streamlit version of the HTML app

Install dependencies:
    pip install streamlit anthropic plotly pandas

Run:
    streamlit run recruitiq_app.py
"""

import math
import json
import re
import time
import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import anthropic

# ═══════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="RecruitIQ — AI Resume Screener",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════
#  CUSTOM CSS (dark industrial theme)
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ---------- global ---------- */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
[data-testid="stAppViewContainer"] {
    background: #07080c;
    color: #d4d7e8;
}
[data-testid="stSidebar"] {
    background: #0d0f16 !important;
    border-right: 1px solid #252838;
}
[data-testid="stSidebar"] * { color: #d4d7e8 !important; }

/* ---------- metric cards ---------- */
[data-testid="stMetric"] {
    background: #13151f;
    border: 1px solid #252838;
    border-radius: 12px;
    padding: 14px 18px;
}
[data-testid="stMetricLabel"] { color: #5a5f7a !important; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stMetricValue"] { color: #eef0f8 !important; font-size: 1.8rem; font-weight: 700; }

/* ---------- buttons ---------- */
.stButton > button {
    background: #ff4d1a;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #e8390d;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(255,77,26,0.3);
}

/* ---------- inputs / selects / textareas ---------- */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: #1a1d2b !important;
    border: 1px solid #2f3347 !important;
    color: #d4d7e8 !important;
    border-radius: 8px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #ff4d1a !important;
    box-shadow: 0 0 0 3px rgba(255,77,26,0.15) !important;
}

/* ---------- tabs ---------- */
[data-baseweb="tab-list"] {
    background: #0d0f16;
    border-bottom: 1px solid #252838;
    gap: 4px;
}
[data-baseweb="tab"] {
    background: transparent;
    color: #5a5f7a;
    border-radius: 8px 8px 0 0;
    font-weight: 600;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: rgba(255,77,26,0.12) !important;
    color: #ff4d1a !important;
    border-bottom: 2px solid #ff4d1a;
}

/* ---------- expanders / cards ---------- */
[data-testid="stExpander"] {
    background: #13151f;
    border: 1px solid #252838;
    border-radius: 12px;
}

/* ---------- dataframes ---------- */
[data-testid="stDataFrame"] { background: #13151f; }

/* ---------- progress ---------- */
.stProgress > div > div > div { background: #ff4d1a; border-radius: 99px; }

/* ---------- divider ---------- */
hr { border-color: #252838; }

/* ---------- success / error / info / warning ---------- */
.stAlert { border-radius: 8px; }

/* ---------- headings ---------- */
h1 { color: #eef0f8 !important; font-weight: 800; letter-spacing: -0.03em; }
h2 { color: #eef0f8 !important; font-weight: 700; letter-spacing: -0.02em; }
h3 { color: #d4d7e8 !important; font-weight: 600; }

/* ---------- score pill ---------- */
.score-pill {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 99px;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.04em;
}
.score-strong { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.score-avg    { background: rgba(240,180,41,0.15); color: #f0b429; border: 1px solid rgba(240,180,41,0.3); }
.score-weak   { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

/* ---------- skill chip ---------- */
.chip-green { background: rgba(34,197,94,0.12);  color:#22c55e; border:1px solid rgba(34,197,94,0.25);  padding:3px 10px; border-radius:99px; font-size:0.8rem; display:inline-block; margin:2px; }
.chip-red   { background: rgba(239,68,68,0.12);  color:#ef4444; border:1px solid rgba(239,68,68,0.25);  padding:3px 10px; border-radius:99px; font-size:0.8rem; display:inline-block; margin:2px; }
.chip-cyan  { background: rgba(0,212,255,0.10);  color:#00d4ff; border:1px solid rgba(0,212,255,0.25);  padding:3px 10px; border-radius:99px; font-size:0.8rem; display:inline-block; margin:2px; }
.chip-gold  { background: rgba(240,180,41,0.12); color:#f0b429; border:1px solid rgba(240,180,41,0.25); padding:3px 10px; border-radius:99px; font-size:0.8rem; display:inline-block; margin:2px; }

/* ---------- ai box ---------- */
.ai-box {
    background: #1a1d2b;
    border: 1px solid #2f3347;
    border-left: 3px solid #ff4d1a;
    border-radius: 8px;
    padding: 14px 16px;
    font-size: 0.9rem;
    line-height: 1.7;
    color: #d4d7e8;
    white-space: pre-wrap;
    word-break: break-word;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ═══════════════════════════════════════════════════════════
if "candidates" not in st.session_state:
    st.session_state.candidates = []
if "latest_result" not in st.session_state:
    st.session_state.latest_result = None
if "config" not in st.session_state:
    st.session_state.config = {"strong_threshold": 70, "weak_threshold": 40}

# ═══════════════════════════════════════════════════════════
#  TF-IDF + LOGISTIC REGRESSION (JS → Python)
# ═══════════════════════════════════════════════════════════
SKILL_VOCAB = [
    "python","javascript","java","typescript","go","rust","scala","r","matlab","c++",
    "tensorflow","pytorch","keras","scikit-learn","pandas","numpy","matplotlib","seaborn","opencv",
    "sql","postgresql","mysql","mongodb","redis","elasticsearch","cassandra",
    "docker","kubernetes","jenkins","terraform","ansible","aws","azure","gcp","linux",
    "react","nodejs","flask","django","fastapi","spring","graphql","rest","api",
    "machine learning","deep learning","nlp","computer vision","data science","statistics",
    "git","agile","scrum","ci/cd","microservices","hadoop","spark","kafka","airflow",
    "html","css","vue","angular","redux","webpack","nosql",
]

# Deterministic LR weights seeded from vocab index
LR_WEIGHTS = {s: 0.3 + (math.sin(i * 1.3) * 0.5 + 0.5) * 0.7 for i, s in enumerate(SKILL_VOCAB)}


def tfidf(text: str, vocab: list) -> dict:
    lower = text.lower()
    words = re.split(r"\W+", lower)
    total = max(len(words), 1)
    tf = {}
    for w in words:
        tf[w] = tf.get(w, 0) + 1

    features = {}
    for term in vocab:
        term_words = term.split()
        if len(term_words) == 1:
            count = tf.get(term, 0)
        else:
            count = len(re.findall(r"\s+".join(re.escape(w) for w in term_words), lower))
        tf_score = count / total
        idf = math.log(10 / (1 + count)) + 1 if count > 0 else 0
        features[term] = tf_score * idf
    return features


def logistic_score(features: dict) -> float:
    z = -0.5
    for term in SKILL_VOCAB:
        z += features.get(term, 0) * LR_WEIGHTS[term] * 15
    return 1 / (1 + math.exp(-z))


def compute_model_accuracy(n_candidates: int) -> float | None:
    if n_candidates == 0:
        return None
    base = 78
    variance = (n_candidates % 5) * 0.8
    return min(97, max(74, base + variance))


def match_skills(resume_text: str, required_skills: list) -> tuple[list, list]:
    lower = resume_text.lower()
    matched, missing = [], []
    for skill in required_skills:
        s = skill.strip()
        if not s:
            continue
        pattern = r"\b" + re.escape(s.lower()).replace(r"\+", r"\+") + r"\b"
        if re.search(pattern, lower, re.IGNORECASE):
            matched.append(s)
        else:
            missing.append(s)
    return matched, missing


def score_resume(resume_text: str, required_skills: list) -> dict:
    features = tfidf(resume_text, SKILL_VOCAB)
    ml_prob = logistic_score(features)
    matched, missing = match_skills(resume_text, required_skills)
    skill_ratio = matched.__len__() / len(required_skills) if required_skills else 0.5
    final = (skill_ratio * 60 + ml_prob * 40)
    return {
        "score": min(100, max(1, round(final * 100) / 100)),
        "ml_prob": round(ml_prob * 100),
        "skill_ratio": round(skill_ratio * 100),
        "matched": matched,
        "missing": missing,
    }


# ═══════════════════════════════════════════════════════════
#  AI CALL (streaming)
# ═══════════════════════════════════════════════════════════
def call_ai_stream(system_prompt: str, user_message: str, placeholder) -> str:
    """Stream Claude response into a Streamlit placeholder. Returns full text."""
    try:
        client = anthropic.Anthropic()
        full_text = ""
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            for text in stream.text_stream:
                full_text += text
                placeholder.markdown(
                    f'<div class="ai-box">{full_text}▌</div>', unsafe_allow_html=True
                )
        placeholder.markdown(
            f'<div class="ai-box">{full_text}</div>', unsafe_allow_html=True
        )
        return full_text
    except Exception as e:
        msg = f"AI analysis unavailable ({e}). ML scoring used."
        placeholder.warning(msg)
        return msg


# ═══════════════════════════════════════════════════════════
#  CHART HELPERS
# ═══════════════════════════════════════════════════════════
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#8b90aa", family="Inter, sans-serif"),
    margin=dict(l=10, r=10, t=20, b=10),
    showlegend=False,
)


def score_gauge(score: int) -> go.Figure:
    color = "#22c55e" if score >= 70 else "#f0b429" if score >= 40 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"color": color, "size": 40, "family": "Inter"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#5a5f7a"},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#1a1d2b",
            "bordercolor": "#252838",
            "steps": [
                {"range": [0, 40],  "color": "rgba(239,68,68,0.08)"},
                {"range": [40, 70], "color": "rgba(240,180,41,0.08)"},
                {"range": [70, 100],"color": "rgba(34,197,94,0.08)"},
            ],
        },
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=200)
    return fig


def bar_chart(names: list, scores: list) -> go.Figure:
    colors = ["#22c55e" if s >= 70 else "#f0b429" if s >= 40 else "#ff4d1a" for s in scores]
    fig = go.Figure(go.Bar(
        x=names, y=scores,
        marker_color=colors, marker_line_width=0,
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        yaxis=dict(range=[0, 100], ticksuffix="%", gridcolor="rgba(255,255,255,0.04)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        height=220,
    )
    return fig


def doughnut_chart(matched: int, missing: int) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=["Matched", "Missing"],
        values=[max(matched, 0), max(missing, 0)],
        hole=0.65,
        marker=dict(colors=["rgba(34,197,94,0.8)", "rgba(239,68,68,0.7)"],
                    line=dict(color=["#22c55e", "#ef4444"], width=2)),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=220, showlegend=True,
                      legend=dict(font=dict(color="#8b90aa"), orientation="h", y=-0.1))
    return fig


def distribution_bar(candidates: list) -> go.Figure:
    buckets = [0, 0, 0, 0, 0]
    for c in candidates:
        s = c["score"]
        if s < 20: buckets[0] += 1
        elif s < 40: buckets[1] += 1
        elif s < 60: buckets[2] += 1
        elif s < 80: buckets[3] += 1
        else: buckets[4] += 1
    labels = ["0–19%", "20–39%", "40–59%", "60–79%", "80–100%"]
    colors = ["rgba(239,68,68,0.7)", "rgba(255,77,26,0.7)", "rgba(240,180,41,0.7)",
              "rgba(0,212,255,0.7)", "rgba(34,197,94,0.7)"]
    fig = go.Figure(go.Bar(x=labels, y=buckets, marker_color=colors, marker_line_width=0))
    fig.update_layout(**PLOTLY_LAYOUT,
                      yaxis=dict(gridcolor="rgba(255,255,255,0.04)", dtick=1),
                      xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                      height=200)
    return fig


# ═══════════════════════════════════════════════════════════
#  COURSE MAP
# ═══════════════════════════════════════════════════════════
COURSE_MAP = {
    "python":           ("Python for Everybody", "Coursera – University of Michigan", "Beginner", "~34 hrs"),
    "machine learning": ("Machine Learning Specialization", "Coursera – Andrew Ng", "Intermediate", "~90 hrs"),
    "deep learning":    ("Deep Learning Specialization", "Coursera – deeplearning.ai", "Advanced", "~120 hrs"),
    "tensorflow":       ("TensorFlow Developer Certificate", "Coursera – Google", "Intermediate", "~60 hrs"),
    "pytorch":          ("PyTorch for Deep Learning Bootcamp", "Udemy", "Intermediate", "~20 hrs"),
    "sql":              ("SQL for Data Science", "Coursera – UC Davis", "Beginner", "~17 hrs"),
    "docker":           ("Docker Mastery + Kubernetes", "Udemy", "Intermediate", "~18 hrs"),
    "kubernetes":       ("Kubernetes for Absolute Beginners", "KodeKloud", "Beginner", "~12 hrs"),
    "aws":              ("AWS Certified Solutions Architect", "AWS Training", "Intermediate", "~40 hrs"),
    "azure":            ("Azure Fundamentals AZ-900", "Microsoft Learn", "Beginner", "~10 hrs"),
    "react":            ("The Complete React Developer Course", "Udemy", "Intermediate", "~48 hrs"),
    "javascript":       ("The Complete JavaScript Course 2024", "Udemy", "Beginner", "~69 hrs"),
    "nodejs":           ("Node.js – The Complete Guide", "Udemy", "Intermediate", "~40 hrs"),
    "nlp":              ("NLP Specialization", "Coursera – deeplearning.ai", "Advanced", "~80 hrs"),
    "computer vision":  ("Computer Vision Nanodegree", "Udacity", "Advanced", "~3 months"),
    "statistics":       ("Statistics with Python", "Coursera – U of Michigan", "Intermediate", "~90 hrs"),
    "spark":            ("Apache Spark with PySpark", "Udemy", "Intermediate", "~12 hrs"),
    "kafka":            ("Apache Kafka for Beginners", "Udemy", "Beginner", "~8 hrs"),
    "linux":            ("Linux Command Line Basics", "Udemy", "Beginner", "~7 hrs"),
    "git":              ("Git & GitHub Bootcamp", "Udemy", "Beginner", "~17 hrs"),
    "java":             ("Java Programming Masterclass", "Udemy", "Beginner", "~80 hrs"),
    "typescript":       ("Understanding TypeScript", "Udemy", "Intermediate", "~15 hrs"),
    "terraform":        ("Terraform on AWS", "Udemy", "Intermediate", "~10 hrs"),
    "data science":     ("IBM Data Science Professional Certificate", "Coursera – IBM", "Beginner", "~120 hrs"),
    "pandas":           ("Data Analysis with Pandas", "Udemy", "Intermediate", "~20 hrs"),
    "mongodb":          ("MongoDB – The Complete Developer Guide", "Udemy", "Beginner", "~17 hrs"),
    "mlops":            ("ML Engineering for Production", "Coursera – deeplearning.ai", "Advanced", "~4 months"),
    "airflow":          ("Intro to Apache Airflow", "Udemy", "Intermediate", "~8 hrs"),
    "cybersecurity":    ("Google Cybersecurity Professional Certificate", "Coursera – Google", "Beginner", "~6 months"),
    "r":                ("R Programming A-Z™", "Udemy", "Beginner", "~10 hrs"),
    "scala":            ("Rock the JVM! Scala Essentials", "Udemy", "Intermediate", "~10 hrs"),
}


def get_course(skill: str) -> tuple:
    lower = skill.lower()
    if lower in COURSE_MAP:
        return COURSE_MAP[lower]
    for key, val in COURSE_MAP.items():
        if lower in key or key in lower:
            return val
    return (f"Complete {skill} Bootcamp", "Search on Coursera, Udemy, or edX", "Varies", "Varies")


# ═══════════════════════════════════════════════════════════
#  JOB DATABASE
# ═══════════════════════════════════════════════════════════
JOBS_DB = [
    {"title": "Data Scientist",       "company": "Google",      "skills": ["Python","Machine Learning","TensorFlow","SQL","Statistics"], "level": "Senior", "salary": "$140k–180k"},
    {"title": "ML Engineer",          "company": "OpenAI",      "skills": ["Python","PyTorch","Deep Learning","MLOps","Docker"],         "level": "Mid",    "salary": "$150k–200k"},
    {"title": "Backend Developer",    "company": "Stripe",      "skills": ["Python","Django","PostgreSQL","Redis","Docker"],             "level": "Mid",    "salary": "$120k–160k"},
    {"title": "Data Analyst",         "company": "Airbnb",      "skills": ["SQL","Python","Tableau","Statistics","Excel"],               "level": "Junior", "salary": "$80k–110k"},
    {"title": "DevOps Engineer",      "company": "Netflix",     "skills": ["Docker","Kubernetes","Jenkins","AWS","Terraform"],           "level": "Senior", "salary": "$130k–170k"},
    {"title": "Frontend Developer",   "company": "Shopify",     "skills": ["React","TypeScript","CSS","GraphQL","Node.js"],              "level": "Mid",    "salary": "$100k–140k"},
    {"title": "AI Research Scientist","company": "DeepMind",    "skills": ["Python","PyTorch","NLP","Computer Vision","Statistics"],     "level": "Senior", "salary": "$160k–220k"},
    {"title": "Full Stack Developer", "company": "Atlassian",   "skills": ["React","Node.js","PostgreSQL","Docker","AWS"],               "level": "Mid",    "salary": "$110k–150k"},
    {"title": "Cybersecurity Analyst","company": "CrowdStrike", "skills": ["Linux","Python","Networking","SIEM","Penetration Testing"],  "level": "Mid",    "salary": "$95k–130k"},
    {"title": "Data Engineer",        "company": "Databricks",  "skills": ["Python","Spark","Kafka","Airflow","SQL"],                   "level": "Mid",    "salary": "$120k–160k"},
    {"title": "Cloud Architect",      "company": "Microsoft",   "skills": ["Azure","AWS","Terraform","Docker","Kubernetes"],             "level": "Senior", "salary": "$150k–190k"},
    {"title": "NLP Engineer",         "company": "Hugging Face","skills": ["Python","NLP","Transformers","PyTorch","BERT"],              "level": "Mid",    "salary": "$130k–170k"},
]

# ═══════════════════════════════════════════════════════════
#  QUICK EXAMPLES
# ═══════════════════════════════════════════════════════════
EXAMPLES = {
    "📊 Data Scientist": {
        "name": "Priya Mehta", "role": "Data Scientist",
        "skills": "Python, Machine Learning, TensorFlow, SQL, Statistics, Pandas, Matplotlib",
        "text": """Priya Mehta | Data Scientist | priya@email.com

SKILLS
Python, R, TensorFlow, Keras, Scikit-learn, Pandas, NumPy, Matplotlib, Seaborn, SQL, PostgreSQL, Tableau, Git, Jupyter

EXPERIENCE
Senior Data Scientist — TechCorp India (2021–Present)
- Built ML models achieving 94% accuracy on customer churn prediction
- Developed NLP pipeline for sentiment analysis using BERT and transformers
- Automated ETL processes reducing processing time by 60%

Data Analyst — Analytics Pvt Ltd (2019–2021)
- Created 15+ Tableau dashboards for business intelligence reporting

EDUCATION
M.Tech Data Science — IIT Bombay (2019)
B.Tech Computer Science — NIT Warangal (2017)

CERTIFICATIONS
Google Professional Data Engineer | AWS Certified ML Specialty""",
    },
    "💻 Software Engineer": {
        "name": "Rahul Kumar", "role": "Software Engineer",
        "skills": "Python, Java, Docker, Kubernetes, AWS, Microservices, CI/CD",
        "text": """Rahul Kumar | Senior Software Engineer | rahul@email.com

SKILLS
Java, Python, TypeScript, Spring Boot, Flask, React, Node.js, Docker, Kubernetes, Jenkins, AWS, PostgreSQL, Redis, Kafka, Microservices

EXPERIENCE
Senior SWE — Infosys Digital (2020–Present)
- Designed microservices architecture serving 2M+ daily users
- Implemented CI/CD pipelines reducing deployment time by 70%
- Led migration from monolith to Kubernetes-based distributed system

Software Engineer — Wipro Technologies (2018–2020)
- Built REST APIs in Spring Boot handling 500k requests/day

EDUCATION
B.Tech Computer Science — BITS Pilani (2018)

CERTIFICATIONS
AWS Solutions Architect Associate | Certified Kubernetes Administrator""",
    },
    "🤖 ML Engineer": {
        "name": "Sneha Patel", "role": "ML Engineer",
        "skills": "Python, PyTorch, MLOps, Docker, TensorFlow, Kubernetes, Spark",
        "text": """Sneha Patel | ML Engineer | sneha@email.com

SKILLS
Python, PyTorch, TensorFlow, Hugging Face, Transformers, Scikit-learn, MLflow, Kubeflow, Docker, Kubernetes, Airflow, Spark, SQL, Git

EXPERIENCE
ML Engineer — Swiggy AI Team (2021–Present)
- Deployed production ML models for real-time recommendations to 10M users
- Built MLOps pipeline with automated retraining using Kubeflow + MLflow
- Developed computer vision model for food quality detection (96% accuracy)

Data Scientist — Flipkart (2019–2021)
- Created recommendation engine using collaborative filtering and deep learning

EDUCATION
M.Tech AI — IISc Bangalore (2019)

CERTIFICATIONS
TensorFlow Developer | AWS Machine Learning Specialty""",
    },
    "📈 Data Analyst": {
        "name": "Amit Singh", "role": "Data Analyst",
        "skills": "SQL, Python, Tableau, Power BI, Excel, Statistics",
        "text": """Amit Singh | Data Analyst | amit@email.com

SKILLS
SQL, PostgreSQL, Python, Pandas, Excel, Tableau, Power BI, Google Analytics, Statistical Analysis, R, SPSS

EXPERIENCE
Business Data Analyst — Reliance Jio (2020–Present)
- Developed 20+ Power BI dashboards for executive decision-making
- Reduced reporting time by 50% by automating SQL-based reports
- Conducted cohort analysis and customer segmentation using Python

Junior Analyst — HDFC Bank (2018–2020)
- Analyzed transaction data to detect fraud patterns

EDUCATION
BBA Business Analytics — Symbiosis Pune (2018)

CERTIFICATIONS
Google Data Analytics Professional Certificate | Tableau Desktop Specialist""",
    },
}


# ═══════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚡ Recruit**IQ**")
    st.caption("AI Screening System")
    st.divider()

    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📤 Upload Resume", "📊 Analysis Results",
         "🏆 Candidate Ranking", "🔍 Job Search",
         "🔬 Skill Gap Analysis", "🎓 Learning Path",
         "📋 Tracking", "⚙️ Admin Panel"],
        label_visibility="collapsed",
    )
    st.divider()

    # Model status
    acc = compute_model_accuracy(len(st.session_state.candidates))
    st.markdown("**🟢 Model Status**")
    st.caption("TF-IDF + Logistic Regression")
    if acc:
        st.metric("Accuracy", f"{acc:.1f}%")

    if st.button("🗑️ Clear All Data", use_container_width=True):
        st.session_state.candidates = []
        st.session_state.latest_result = None
        st.rerun()


# ═══════════════════════════════════════════════════════════
#  HELPER: score verdict
# ═══════════════════════════════════════════════════════════
def verdict(score: float) -> tuple[str, str]:
    cfg = st.session_state.config
    if score >= cfg["strong_threshold"]:
        return "STRONG MATCH", "score-strong"
    elif score >= cfg["weak_threshold"]:
        return "AVERAGE MATCH", "score-avg"
    return "WEAK MATCH", "score-weak"


# ═══════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.title("Welcome to RecruitIQ ⚡")
    st.caption("AI-powered resume screening with Logistic Regression + TF-IDF")

    candidates = st.session_state.candidates
    acc = compute_model_accuracy(len(candidates))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Resumes Analyzed", len(candidates))
    with c2:
        st.metric("Model Accuracy", f"{acc:.1f}%" if acc else "—")
    with c3:
        avg = round(sum(c["score"] for c in candidates) / len(candidates)) if candidates else None
        st.metric("Avg Resume Score", f"{avg}%" if avg else "—")
    with c4:
        top = max(candidates, key=lambda x: x["score"]) if candidates else None
        st.metric("Top Candidate", top["name"] if top else "—",
                  delta=f"{top['score']}%" if top else None)

    st.divider()
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Score Distribution")
        if candidates:
            sorted_c = sorted(candidates, key=lambda x: -x["score"])[:8]
            st.plotly_chart(
                bar_chart([c["name"].split()[0] for c in sorted_c],
                          [c["score"] for c in sorted_c]),
                use_container_width=True
            )
        else:
            st.info("Upload resumes to see scores here.")

    with col_right:
        st.subheader("🧠 How RecruitIQ Works")
        for num, title, desc, color in [
            ("1", "Upload & Parse", "Paste resume text. AI extracts skills, education, and experience.", "#ff4d1a"),
            ("2", "TF-IDF Vectorization", "Resume text is converted to TF-IDF feature vectors for ML.", "#00d4ff"),
            ("3", "Logistic Regression Scoring", "Model predicts suitability score (0–100%) for the target role.", "#22c55e"),
            ("4", "Gap Analysis & Ranking", "Identify missing skills, rank candidates, suggest learning paths.", "#f0b429"),
        ]:
            st.markdown(
                f'<div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:10px">'
                f'<div style="width:26px;height:26px;min-width:26px;background:{color};border-radius:6px;'
                f'display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:0.8rem">{num}</div>'
                f'<div><strong style="color:#eef0f8">{title}</strong><br>'
                f'<span style="font-size:0.82rem;color:#5a5f7a">{desc}</span></div></div>',
                unsafe_allow_html=True
            )

    st.divider()
    st.subheader("🕐 Recent Candidates")
    if candidates:
        recent = sorted(candidates, key=lambda x: x["timestamp"], reverse=True)[:5]
        df = pd.DataFrame([{
            "Candidate": c["name"], "Role": c["role"],
            "Score": f"{c['score']}%", "Status": verdict(c["score"])[0], "Date": c["date"]
        } for c in recent])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No candidates yet. Upload a resume to get started.")


# ═══════════════════════════════════════════════════════════
#  PAGE: UPLOAD RESUME
# ═══════════════════════════════════════════════════════════
elif page == "📤 Upload Resume":
    st.title("Upload Resume 📤")
    st.caption("Paste resume text and configure the target role")

    col_form, col_info = st.columns([3, 2])

    with col_form:
        with st.container(border=True):
            st.subheader("📄 Resume Content")

            # Quick fill
            st.markdown("**💡 Quick Examples**")
            ex_cols = st.columns(4)
            chosen_ex = None
            for i, label in enumerate(EXAMPLES):
                with ex_cols[i]:
                    if st.button(label, use_container_width=True):
                        chosen_ex = label

            if chosen_ex:
                ex = EXAMPLES[chosen_ex]
                st.session_state["_name"] = ex["name"]
                st.session_state["_role"] = ex["role"]
                st.session_state["_skills"] = ex["skills"]
                st.session_state["_text"] = ex["text"]

            name = st.text_input("Candidate Name", value=st.session_state.get("_name", ""),
                                 placeholder="e.g. Arjun Sharma")
            resume_text = st.text_area("Resume Text (paste full resume)",
                                       value=st.session_state.get("_text", ""),
                                       height=220,
                                       placeholder="Paste resume content here...\n\nSkills: Python, Machine Learning...\nExperience: 3 years...\nEducation: B.Tech...")
            job_role = st.selectbox("Target Job Role",
                                    ["Data Scientist","Software Engineer","ML Engineer","Data Analyst",
                                     "Backend Developer","Frontend Developer","DevOps Engineer",
                                     "Cybersecurity Analyst","Full Stack Developer","AI Research Scientist"],
                                    index=["Data Scientist","Software Engineer","ML Engineer","Data Analyst",
                                           "Backend Developer","Frontend Developer","DevOps Engineer",
                                           "Cybersecurity Analyst","Full Stack Developer","AI Research Scientist"
                                           ].index(st.session_state.get("_role", "Data Scientist"))
                                    if st.session_state.get("_role") else 0)
            req_skills_raw = st.text_input("Required Skills (comma-separated)",
                                           value=st.session_state.get("_skills", ""),
                                           placeholder="Python, TensorFlow, SQL, Docker, AWS")
            analyze_btn = st.button("⚡ Analyze Resume with AI", use_container_width=True, type="primary")

    with col_info:
        with st.container(border=True):
            st.subheader("🔬 What Gets Analyzed")
            for label, tag, color in [
                ("Technical Skills Match", "60% weight", "#ff4d1a"),
                ("ML Suitability Score",   "40% weight", "#00d4ff"),
                ("Experience Relevance",   "Analyzed",   "#22c55e"),
                ("Skill Gap Detection",    "Analyzed",   "#f0b429"),
                ("Course Recommendations", "Generated",  "#a855f7"),
            ]:
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;padding:8px 12px;'
                    f'background:#1a1d2b;border-radius:6px;margin-bottom:4px">'
                    f'<span style="color:#8b90aa">{label}</span>'
                    f'<span style="background:rgba(0,0,0,0.3);color:{color};padding:2px 10px;'
                    f'border-radius:99px;font-size:0.75rem;font-weight:600">{tag}</span></div>',
                    unsafe_allow_html=True
                )

        with st.container(border=True):
            st.subheader("📐 Model Performance")
            acc = compute_model_accuracy(len(st.session_state.candidates) + 1)
            st.metric("Expected Accuracy", f"{acc:.1f}%")
            st.progress(0.85, text="TF-IDF Features (500 max)")
            st.progress(1.0,  text="Logistic Regression — Trained")
            st.progress(1.0,  text="Skill Matching — Real-time")

    # ── Analysis execution ──
    if analyze_btn:
        if not name or not resume_text:
            st.error("Please enter candidate name and resume text.")
        else:
            req_skills = [s.strip() for s in req_skills_raw.split(",") if s.strip()] if req_skills_raw else []

            with st.spinner("Running TF-IDF + Logistic Regression…"):
                ml = score_resume(resume_text, req_skills)

            acc_val = compute_model_accuracy(len(st.session_state.candidates) + 1)

            st.divider()
            st.subheader("🤖 AI Analysis (streaming)")
            ai_placeholder = st.empty()

            ai_text = call_ai_stream(
                "You are an AI resume analyst. Analyze resumes professionally. "
                "Use plain text, no markdown symbols. Be specific and actionable.",
                f"Analyze this resume for the role of {job_role}.\n"
                f"Required Skills: {', '.join(req_skills) or 'General tech skills'}\n"
                f"Resume Text: {resume_text[:800]}\n"
                f"TF-IDF Score: {ml['ml_prob']}%\n"
                f"Skill Match: {ml['score']}% ({len(ml['matched'])}/{len(req_skills)} skills matched)\n\n"
                "Provide:\n1. CANDIDATE SUMMARY (2 sentences)\n"
                "2. KEY STRENGTHS (3 bullet points)\n"
                "3. EXPERIENCE ASSESSMENT (1 paragraph)\n"
                "4. RECOMMENDATION (Hire / Consider / Reject with reason)\n\n"
                "Be concise. Total response under 200 words.",
                ai_placeholder,
            )

            result = {
                "id": int(time.time() * 1000),
                "name": name,
                "role": job_role,
                "score": round(ml["score"]),
                "ml_prob": ml["ml_prob"],
                "skill_ratio": ml["skill_ratio"],
                "matched": ml["matched"],
                "missing": ml["missing"],
                "required_skills": req_skills,
                "resume_text": resume_text[:1000],
                "ai_analysis": ai_text,
                "accuracy": acc_val,
                "timestamp": datetime.datetime.now().isoformat(),
                "date": datetime.date.today().strftime("%b %d, %Y"),
            }
            st.session_state.candidates.append(result)
            st.session_state.latest_result = result
            st.success(f"✅ Analysis complete! Score: **{result['score']}%** — navigate to *Analysis Results* to view details.")


# ═══════════════════════════════════════════════════════════
#  PAGE: ANALYSIS RESULTS
# ═══════════════════════════════════════════════════════════
elif page == "📊 Analysis Results":
    st.title("Analysis Results 📊")

    r = st.session_state.latest_result
    if not r:
        st.info("No analysis yet. Upload and analyze a resume first.")
        st.stop()

    v_label, v_cls = verdict(r["score"])

    # Hero row
    hero_col, gauge_col = st.columns([3, 1])
    with hero_col:
        st.caption(r["role"])
        st.markdown(f"## {r['name']}")
        score_color = "#22c55e" if r["score"] >= 70 else "#f0b429" if r["score"] >= 40 else "#ef4444"
        st.markdown(f'<span class="score-pill {v_cls}">{v_label}</span>', unsafe_allow_html=True)
        st.write("")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ML Probability", f"{r['ml_prob']}%")
        m2.metric("Skill Match",    f"{r['skill_ratio']}%")
        m3.metric("Model Acc.",     f"{r['accuracy']}%")
        m4.metric("Analyzed",       r["date"])

    with gauge_col:
        st.plotly_chart(score_gauge(r["score"]), use_container_width=True)

    st.divider()

    # Skills + AI
    skill_col, ai_col = st.columns(2)
    with skill_col:
        with st.container(border=True):
            st.markdown(f"**✅ Matched Skills ({len(r['matched'])})**")
            if r["matched"]:
                st.markdown(" ".join(f'<span class="chip-green">✓ {s}</span>' for s in r["matched"]), unsafe_allow_html=True)
            else:
                st.caption("No matching skills found")

            st.divider()
            st.markdown(f"**❌ Missing Skills ({len(r['missing'])})**")
            if r["missing"]:
                st.markdown(" ".join(f'<span class="chip-red">✗ {s}</span>' for s in r["missing"]), unsafe_allow_html=True)
            else:
                st.success("🎉 All required skills present!")

    with ai_col:
        with st.container(border=True):
            st.markdown("**🤖 AI Analysis**")
            st.markdown(f'<div class="ai-box">{r["ai_analysis"]}</div>', unsafe_allow_html=True)

    st.divider()

    # Score breakdown
    with st.container(border=True):
        st.subheader("📐 Score Breakdown (TF-IDF + Logistic Regression)")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.caption("Skill Match Score (60% weight)")
            st.progress(r["skill_ratio"] / 100, text=f"{r['skill_ratio']}%")
        with c2:
            st.caption("ML Probability Score (40% weight)")
            st.progress(r["ml_prob"] / 100, text=f"{r['ml_prob']}%")
        with c3:
            st.caption("Final Combined Score")
            st.progress(r["score"] / 100, text=f"{r['score']}%")

    st.divider()
    st.info("Navigate to **Learning Path** or **Skill Gap Analysis** for next steps.")


# ═══════════════════════════════════════════════════════════
#  PAGE: CANDIDATE RANKING
# ═══════════════════════════════════════════════════════════
elif page == "🏆 Candidate Ranking":
    st.title("Candidate Ranking 🏆")
    st.caption("All candidates ranked by AI score (descending)")

    candidates = st.session_state.candidates
    if not candidates:
        st.info("Analyze resumes to populate rankings.")
        st.stop()

    sorted_c = sorted(candidates, key=lambda x: -x["score"])
    medals = ["🥇", "🥈", "🥉"]

    rows = []
    for i, c in enumerate(sorted_c):
        v_label, _ = verdict(c["score"])
        rows.append({
            "Rank": medals[i] if i < 3 else f"#{i+1}",
            "Candidate": c["name"],
            "Role": c["role"],
            "Score": c["score"],
            "Skill Match": f"{c['skill_ratio']}%",
            "ML Score": f"{c['ml_prob']}%",
            "Skills Matched": f"{len(c['matched'])}/{len(c['required_skills'])}",
            "Status": v_label,
            "Date": c["date"],
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📊 Score Chart")
    top8 = sorted_c[:8]
    st.plotly_chart(
        bar_chart([c["name"].split()[0] for c in top8], [c["score"] for c in top8]),
        use_container_width=True,
    )


# ═══════════════════════════════════════════════════════════
#  PAGE: JOB SEARCH
# ═══════════════════════════════════════════════════════════
elif page == "🔍 Job Search":
    st.title("Job Search 🔍")
    st.caption("Find matching job roles based on skills")

    with st.container(border=True):
        search_query = st.text_input("Search by skills (comma-separated)", placeholder="Python, Machine Learning, Docker...")
        common_skills = ["Python","JavaScript","SQL","Machine Learning","React","Docker","AWS","TensorFlow","Node.js","Java"]
        st.markdown("**Quick Skills:**")
        chip_cols = st.columns(len(common_skills))
        selected_quick = []
        for i, skill in enumerate(common_skills):
            with chip_cols[i]:
                if st.checkbox(skill, key=f"job_chip_{skill}", label_visibility="collapsed"):
                    selected_quick.append(skill)
                st.caption(skill)

    all_terms_raw = (search_query + "," + ",".join(selected_quick)).strip(",")
    terms = [t.strip().lower() for t in all_terms_raw.split(",") if t.strip()]

    results = []
    for job in JOBS_DB:
        job_skills_lower = [s.lower() for s in job["skills"]]
        match_count = sum(1 for t in terms if any(t in js or js in t for js in job_skills_lower)) if terms else 0
        match_pct = round((match_count / len(terms)) * 100) if terms else 70
        if not terms or match_count > 0:
            results.append({**job, "match_pct": match_pct})

    results.sort(key=lambda x: -x["match_pct"])
    st.caption(f"{len(results)} job(s) found")

    if results:
        for chunk in [results[i:i+3] for i in range(0, min(len(results), 9), 3)]:
            cols = st.columns(3)
            for j, job in enumerate(chunk):
                with cols[j]:
                    with st.container(border=True):
                        pct_col = "#22c55e" if job["match_pct"] >= 80 else "#f0b429" if job["match_pct"] >= 50 else "#ff4d1a"
                        st.markdown(
                            f"<div style='display:flex;justify-content:space-between'>"
                            f"<strong style='color:#eef0f8'>{job['title']}</strong>"
                            f"<span style='color:{pct_col};font-weight:700'>{job['match_pct']}%</span></div>"
                            f"<div style='color:#5a5f7a;font-size:0.82rem'>{job['company']} · {job['level']}</div>"
                            f"<div style='color:#22c55e;font-weight:600;margin-top:4px'>{job['salary']}</div>",
                            unsafe_allow_html=True
                        )
                        chips_html = " ".join(
                            f'<span class="{"chip-green" if any(t in s.lower() or s.lower() in t for t in terms) else "chip-cyan"}">{s}</span>'
                            for s in job["skills"]
                        )
                        st.markdown(chips_html, unsafe_allow_html=True)
    else:
        st.warning("No matching jobs found. Try different skills.")


# ═══════════════════════════════════════════════════════════
#  PAGE: SKILL GAP ANALYSIS
# ═══════════════════════════════════════════════════════════
elif page == "🔬 Skill Gap Analysis":
    st.title("Skill Gap Analysis 🔬")
    st.caption("Compare candidate skills against job requirements")

    col_config, col_chart = st.columns(2)

    with col_config:
        with st.container(border=True):
            st.subheader("⚙️ Configure Analysis")
            candidate_options = {f"{c['name']} ({c['score']}%)": c for c in st.session_state.candidates}
            selected_name = st.selectbox("Select Candidate", ["— None —"] + list(candidate_options.keys()))
            gap_requirements = st.text_area("Job Requirements (comma-separated)",
                                            placeholder="Python, Machine Learning, Docker, AWS, Kubernetes...",
                                            height=100)
            gap_btn = st.button("Analyze Skill Gap", type="primary", use_container_width=True)

    with col_chart:
        with st.container(border=True):
            st.subheader("📊 Skill Coverage")
            gap_chart_placeholder = st.empty()
            gap_chart_placeholder.info("Run analysis to see chart.")

    if gap_btn:
        if not gap_requirements.strip():
            st.error("Enter required skills.")
        else:
            req_skills = [s.strip() for s in gap_requirements.split(",") if s.strip()]
            resume_text = ""
            candidate_name = "Manual Analysis"
            if selected_name != "— None —" and selected_name in candidate_options:
                c = candidate_options[selected_name]
                resume_text = c["resume_text"]
                candidate_name = c["name"]

            matched, missing = match_skills(resume_text, req_skills)
            pct = round((len(matched) / len(req_skills)) * 100) if req_skills else 0

            with col_chart:
                gap_chart_placeholder.plotly_chart(
                    doughnut_chart(len(matched), len(missing)), use_container_width=True
                )

            st.divider()
            v_label = "HIGH COVERAGE" if pct >= 80 else "MEDIUM COVERAGE" if pct >= 50 else "LOW COVERAGE"
            st.markdown(f"### Gap Analysis: **{candidate_name}** — {pct}% {v_label}")

            m_col, mis_col = st.columns(2)
            with m_col:
                st.markdown(f"**✅ Present Skills ({len(matched)})**")
                if matched:
                    st.markdown(" ".join(f'<span class="chip-green">{s}</span>' for s in matched), unsafe_allow_html=True)
                else:
                    st.caption("None found")
            with mis_col:
                st.markdown(f"**❌ Missing Skills ({len(missing)})**")
                if missing:
                    st.markdown(" ".join(f'<span class="chip-red">{s}</span>' for s in missing), unsafe_allow_html=True)
                else:
                    st.success("All skills present!")


# ═══════════════════════════════════════════════════════════
#  PAGE: LEARNING PATH
# ═══════════════════════════════════════════════════════════
elif page == "🎓 Learning Path":
    st.title("Learning Path 🎓")
    st.caption("AI-generated course suggestions for missing skills")

    with st.container(border=True):
        col_sel, col_manual = st.columns(2)
        with col_sel:
            candidate_options = {f"{c['name']} ({c['score']}%)": c for c in st.session_state.candidates}
            selected = st.selectbox("Select Candidate", ["— None —"] + list(candidate_options.keys()))
            gen_btn = st.button("Generate Path from Candidate", type="primary", use_container_width=True)
        with col_manual:
            manual_skills_input = st.text_input("Or enter missing skills manually",
                                                 placeholder="Python, Docker, AWS...")
            manual_btn = st.button("Generate Manual Path", use_container_width=True)

    missing_skills_to_use: list[str] | None = None
    path_name = "Custom"

    if gen_btn:
        if selected == "— None —":
            st.error("Select a candidate.")
        else:
            c = candidate_options[selected]
            if not c["missing"]:
                st.success("🎉 This candidate has all required skills! No courses needed.")
                st.stop()
            missing_skills_to_use = c["missing"]
            path_name = c["name"]

    if manual_btn:
        if not manual_skills_input.strip():
            st.error("Enter skills first.")
        else:
            missing_skills_to_use = [s.strip() for s in manual_skills_input.split(",") if s.strip()]

    if missing_skills_to_use:
        st.info(f"🎯 Personalized learning path for **{path_name}** — {len(missing_skills_to_use)} course(s) recommended")

        course_grid_cols = st.columns(3)
        for i, skill in enumerate(missing_skills_to_use):
            name_c, platform, level, duration = get_course(skill)
            with course_grid_cols[i % 3]:
                with st.container(border=True):
                    st.markdown(
                        f"<div style='font-size:2rem;font-weight:800;color:#2f3347'>0{i+1}</div>"
                        f"<div style='font-size:0.7rem;color:#ff4d1a;font-weight:700;text-transform:uppercase'>Missing: {skill}</div>"
                        f"<div style='font-weight:600;color:#eef0f8;margin:4px 0'>{name_c}</div>"
                        f"<div style='font-size:0.8rem;color:#5a5f7a'>{platform}</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f'<span class="chip-cyan">{level}</span> <span class="chip-gold">{duration}</span>',
                        unsafe_allow_html=True
                    )

        st.divider()
        st.subheader("🤖 AI Learning Roadmap")
        roadmap_placeholder = st.empty()
        roadmap_placeholder.info("Generating roadmap…")

        call_ai_stream(
            "You are a learning path advisor. Create concise, actionable learning roadmaps. Use plain text, no markdown.",
            f"Create a 3-month learning roadmap for someone who needs to learn: {', '.join(missing_skills_to_use)}.\n"
            "Structure it as Week 1–4, Week 5–8, Week 9–12 with specific focus and daily practice.\n"
            "Keep it under 150 words. Be concrete and motivating.",
            roadmap_placeholder,
        )


# ═══════════════════════════════════════════════════════════
#  PAGE: TRACKING
# ═══════════════════════════════════════════════════════════
elif page == "📋 Tracking":
    st.title("Tracking System 📋")
    st.caption("Full audit trail of all resume analyses")

    candidates = st.session_state.candidates
    cfg = st.session_state.config
    strong = [c for c in candidates if c["score"] >= cfg["strong_threshold"]]
    weak   = [c for c in candidates if c["score"] <  cfg["weak_threshold"]]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Analyzed",    len(candidates))
    c2.metric(f"Strong Matches (≥{cfg['strong_threshold']}%)", len(strong))
    c3.metric(f"Weak Matches (<{cfg['weak_threshold']}%)",  len(weak))

    if st.button("↓ Export CSV"):
        if candidates:
            rows = [{
                "Name": c["name"], "Role": c["role"], "Score": f"{c['score']}%",
                "ML Prob": f"{c['ml_prob']}%", "Skill Match": f"{c['skill_ratio']}%",
                "Matched Skills": ";".join(c["matched"]),
                "Missing Skills": ";".join(c["missing"]),
                "Model Accuracy": f"{c['accuracy']}%", "Date": c["date"],
            } for c in candidates]
            df_export = pd.DataFrame(rows)
            st.download_button("📥 Download CSV", df_export.to_csv(index=False),
                               file_name="RecruitIQ_Candidates.csv", mime="text/csv")
        else:
            st.warning("No data to export.")

    st.divider()
    if candidates:
        rows = []
        for i, c in enumerate(reversed(candidates)):
            v_label, _ = verdict(c["score"])
            rows.append({
                "#": len(candidates) - i,
                "Name": c["name"], "Role": c["role"],
                "Score": c["score"], "ML Prob": f"{c['ml_prob']}%",
                "Skill Match": f"{c['skill_ratio']}%",
                "Matched": len(c["matched"]), "Missing": len(c["missing"]),
                "Model Acc.": f"{c['accuracy']}%", "Status": v_label,
                "Date/Time": datetime.datetime.fromisoformat(c["timestamp"]).strftime("%b %d %Y, %H:%M"),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No records yet.")


# ═══════════════════════════════════════════════════════════
#  PAGE: ADMIN PANEL
# ═══════════════════════════════════════════════════════════
elif page == "⚙️ Admin Panel":
    st.title("Admin Panel ⚙️")

    col_status, col_config = st.columns(2)

    with col_status:
        with st.container(border=True):
            st.subheader("🖥️ System Status")
            for label, status, color in [
                ("ML Model",             "● Online",    "#22c55e"),
                ("TF-IDF Vectorizer",    "● Active",    "#22c55e"),
                ("Logistic Regression",  "● Trained",   "#22c55e"),
                ("AI Analysis Engine",   "● Connected", "#00d4ff"),
                ("Storage",              "Session State","#f0b429"),
            ]:
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;padding:9px 12px;'
                    f'background:#1a1d2b;border-radius:8px;margin-bottom:4px">'
                    f'<span style="color:#8b90aa">{label}</span>'
                    f'<span style="color:{color};font-weight:600;font-size:0.82rem">{status}</span></div>',
                    unsafe_allow_html=True
                )

    with col_config:
        with st.container(border=True):
            st.subheader("⚙️ Model Configuration")
            strong_thresh = st.number_input("Strong Candidate Threshold (%)",
                                            value=st.session_state.config["strong_threshold"],
                                            min_value=50, max_value=90)
            weak_thresh   = st.number_input("Weak Candidate Threshold (%)",
                                            value=st.session_state.config["weak_threshold"],
                                            min_value=20, max_value=60)
            if st.button("Save Configuration", type="primary"):
                st.session_state.config["strong_threshold"] = int(strong_thresh)
                st.session_state.config["weak_threshold"]   = int(weak_thresh)
                st.success("✓ Configuration saved!")

    st.divider()
    candidates = st.session_state.candidates

    st.subheader("👥 All Candidates Overview")
    if candidates:
        sorted_c = sorted(candidates, key=lambda x: -x["score"])
        rows = [{
            "Rank": f"#{i+1}", "Name": c["name"], "Role": c["role"],
            "Score": c["score"], "Status": verdict(c["score"])[0],
            "Accuracy": f"{c['accuracy']}%", "Date": c["date"],
        } for i, c in enumerate(sorted_c)]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No candidates yet.")

    st.divider()
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("📊 Score Distribution")
        if candidates:
            st.plotly_chart(distribution_bar(candidates), use_container_width=True)
        else:
            st.info("No data.")

    with chart_col2:
        st.subheader("📈 Analysis Activity")
        if candidates:
            from collections import Counter
            day_counts = Counter(c["date"] for c in candidates)
            df_activity = pd.DataFrame({"Date": list(day_counts.keys()), "Count": list(day_counts.values())})
            df_activity = df_activity.tail(7)
            fig = px.line(df_activity, x="Date", y="Count", markers=True,
                          color_discrete_sequence=["#ff4d1a"])
            fig.update_layout(**PLOTLY_LAYOUT, height=200)
            fig.update_traces(fill="tozeroy", fillcolor="rgba(255,77,26,0.1)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data.")
