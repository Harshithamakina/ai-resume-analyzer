import re
from parser import SKILLS

def calculate_score(resume_data: dict, job_description: str) -> dict:
    jd = job_description.lower().strip()
    resume_skills = [s.lower() for s in resume_data.get("skills", [])]

    # ── Skills (50 pts) ──────────────────────────────────────
    matched = []
    missing = []

    for skill in resume_skills:
        if skill in jd:
            matched.append(skill.title())

    for skill in SKILLS:
        if skill in jd and skill not in resume_skills:
            missing.append(skill.title())

    if not resume_skills:
        skill_score = 0
    elif not jd:
        skill_score = 25
    else:
        skill_score = min(50, int((len(matched) / len(resume_skills)) * 50))

    # ── Education (20 pts) ───────────────────────────────────
    edu_score = 20 if resume_data.get("education") else 5

    # ── Experience (20 pts) ──────────────────────────────────
    exp = resume_data.get("experience_years", 0)
    jd_exp = re.search(r'(\d+)\+?\s*years?', jd)
    req = float(jd_exp.group(1)) if jd_exp else 0
    if req == 0:
        exp_score = 15
    elif exp >= req:
        exp_score = 20
    else:
        exp_score = max(5, int((exp / req) * 20))

    # ── Contact (10 pts) ─────────────────────────────────────
    contact_score = 0
    if resume_data.get("email") != "Not found":   contact_score += 4
    if resume_data.get("phone") != "Not found":   contact_score += 3
    if resume_data.get("linkedin") != "Not found": contact_score += 2
    if resume_data.get("github") != "Not found":   contact_score += 1

    total = min(100, skill_score + edu_score + exp_score + contact_score)

    extra = [s.title() for s in resume_skills if s not in jd]

    return {
        "total": total,
        "breakdown": {
            "Skills match": skill_score,
            "Education":    edu_score,
            "Experience":   exp_score,
            "Contact info": contact_score,
        },
        "matched": matched,
        "missing": missing[:12],
        "extra":   extra[:8],
        "label":   _label(total),
        "color":   _color(total),
    }

def _label(score):
    if score >= 80: return "Excellent Match"
    if score >= 60: return "Good Match"
    if score >= 40: return "Partial Match"
    return "Low Match"

def _color(score):
    if score >= 80: return "green"
    if score >= 60: return "blue"
    if score >= 40: return "orange"
    return "red"
