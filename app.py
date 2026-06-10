import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from parser import parse_resume
from scorer import calculate_score
from feedback import get_ai_feedback
from database import init, save, get_all

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Init DB ───────────────────────────────────────────────────
init()

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #666;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .score-box {
        text-align: center;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .skill-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 3px;
        font-size: 0.85rem;
    }
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        margin: 1rem 0 0.5rem 0;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/resume.png", width=60)
    st.title("AI Resume Analyzer")
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("1. Upload your PDF resume")
    st.markdown("2. Paste a job description")
    st.markdown("3. Get ATS score + skill gap")
    st.markdown("4. Get AI-powered feedback")
    st.markdown("---")

    
# ── Main Header ───────────────────────────────────────────────
st.markdown('<div class="main-header">📄 AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your resume · Get ATS score · Fix skill gaps · Land the job</div>', unsafe_allow_html=True)

# ── Input Section ─────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📤 Upload Resume")
    uploaded = st.file_uploader("PDF only · Max 10MB", type=["pdf"])

    st.subheader("📋 Job Description")
    job_title = st.text_input("Job title (optional)", placeholder="e.g. Python Backend Developer")
    jd = st.text_area(
        "Paste job description here",
        height=220,
        placeholder="Example:\nWe are looking for a Python Backend Developer with 2+ years of experience in Django, PostgreSQL, Docker, Redis...\n\nRequirements:\n- Strong Python skills\n- Experience with REST APIs\n- Knowledge of databases..."
    )

    use_ai = st.checkbox("Generate AI feedback", value=True)
    analyze_btn = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

# ── Analysis ──────────────────────────────────────────────────
if analyze_btn:
    if not uploaded:
        st.error("Please upload a PDF resume first.")
        st.stop()

    with st.spinner("Parsing resume..."):
        data = parse_resume(uploaded)

    with st.spinner("Calculating ATS score..."):
        score = calculate_score(data, jd)

    # Save to history
    save(data["name"], data["email"], score["total"],
         score["label"], data["skills"], job_title)

    with col_right:
        # ── Candidate Info ────────────────────────────────────
        st.subheader("👤 Candidate Info")
        c1, c2 = st.columns(2)
        c1.metric("Name", data["name"])
        c2.metric("Email", data["email"])
        c1.metric("Phone", data["phone"])
        c2.metric("Experience", f"{data['experience_years']} yrs")

        # ── ATS Score ─────────────────────────────────────────
        st.subheader("🎯 ATS Score")
        color_map = {"green": "#1D9E75", "blue": "#378ADD", "orange": "#EF9F27", "red": "#E24B4A"}
        color = color_map[score["color"]]

        score_col, label_col = st.columns([1, 2])
        with score_col:
            st.markdown(
                f'<div style="text-align:center;padding:1rem;background:#f8f9fa;border-radius:12px">'
                f'<div style="font-size:3rem;font-weight:700;color:{color}">{score["total"]}</div>'
                f'<div style="color:#666;font-size:0.85rem">out of 100</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with label_col:
            st.markdown(f"### {score['label']}")
            st.progress(score["total"] / 100)

        # ── Score Breakdown ───────────────────────────────────
        st.subheader("📊 Score Breakdown")
        breakdown_df = pd.DataFrame(
            list(score["breakdown"].items()),
            columns=["Category", "Score"]
        )
        breakdown_df["Max"] = [50, 20, 20, 10]
        breakdown_df["Percentage"] = (breakdown_df["Score"] / breakdown_df["Max"] * 100).round(0).astype(int)
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

    # ── Skills Section ────────────────────────────────────────
    st.divider()
    sk1, sk2, sk3 = st.columns(3)

    with sk1:
        st.markdown("### ✅ Skills in Resume")
        if data["skills"]:
            skills_html = ""
            for s in data["skills"]:
                skills_html += f'<span style="background:#e8f5e9;color:#1b5e20;padding:3px 10px;border-radius:12px;margin:3px;display:inline-block;font-size:0.82rem">{s}</span>'
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.info("No skills detected. Make sure your PDF text is readable (not a scanned image).")

    with sk2:
        st.markdown("### 🟢 Matched with JD")
        if score["matched"]:
            for s in score["matched"]:
                st.success(s)
        elif not jd.strip():
            st.info("Paste a job description to see matches.")
        else:
            st.warning("No matching skills found.")

    with sk3:
        st.markdown("### 🔴 Missing — Add These")
        if score["missing"]:
            for s in score["missing"]:
                st.error(s)
            st.caption("Adding these keywords can boost your ATS score by 10-15 points.")
        else:
            st.success("You have all required skills!")

    # ── Education ─────────────────────────────────────────────
    st.divider()
    ed_col, links_col = st.columns(2)

    with ed_col:
        st.markdown("### 🎓 Education Detected")
        if data["education"]:
            for e in data["education"]:
                st.write(f"• {e}")
        else:
            st.info("No education info detected.")

    with links_col:
        st.markdown("### 🔗 Links Found")
        st.write(f"**LinkedIn:** {data['linkedin']}")
        st.write(f"**GitHub:** {data['github']}")

    # ── AI Feedback ───────────────────────────────────────────
    st.divider()
    st.subheader("🤖 AI Feedback")

    if use_ai:
        with st.spinner("Generating AI feedback... (10-15 seconds)"):
            feedback = get_ai_feedback(
                data["raw_text"], jd,
                score["total"], score["matched"], score["missing"]
            )
        st.markdown(feedback)
    else:
        st.info("Enable AI feedback checkbox above to get detailed suggestions.")

    # ── Raw Text Preview ──────────────────────────────────────
    with st.expander("📄 View Extracted Resume Text"):
        st.text(data["raw_text"][:3000] + ("..." if len(data["raw_text"]) > 3000 else ""))

# ── History ───────────────────────────────────────────────────
st.divider()
with st.expander("📚 Analysis History"):
    rows = get_all()
    if rows:
        df = pd.DataFrame(rows, columns=["Name", "Email", "Score", "Label", "Job Title", "Time"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No analyses yet. Upload a resume to get started.")
