import os
from dotenv import load_dotenv
load_dotenv()

def get_ai_feedback(resume_text: str, job_description: str, score: int,
                    matched: list, missing: list) -> str:

    api_key = os.getenv("GROQ_API_KEY", "")

    if api_key:
        try:
            from groq import Groq
            client = Groq(api_key=api_key)

            prompt = f"""You are a senior HR consultant and resume coach.
Analyze this resume against the job description below.

RESUME (first 2000 chars):
{resume_text[:2000]}

JOB DESCRIPTION:
{job_description[:1000]}

ATS SCORE: {score}/100
MATCHED SKILLS: {', '.join(matched) or 'None'}
MISSING SKILLS: {', '.join(missing) or 'None'}

Give your analysis in this exact format:

## Overall Assessment
[2-3 sentences on overall fit for this role]

## Top 3 Strengths
1. [Specific strength]
2. [Specific strength]
3. [Specific strength]

## Top 3 Gaps to Fix
1. [Gap + how to fix it specifically]
2. [Gap + how to fix it specifically]
3. [Gap + how to fix it specifically]

## Keywords to Add to Resume
[List 5-6 specific keywords from the JD not in resume]

## Priority Action Items
1. [Most important thing to do first]
2. [Second most important]
3. [Third most important]

## Interview Readiness
[Ready / Needs 2-4 Weeks / Not Ready Yet] — [1 sentence reason]

Be specific, actionable, and encouraging."""

            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
            )
            return response.choices[0].message.content

        except Exception as e:
            return _rule_based(score, matched, missing)
    else:
        return _rule_based(score, matched, missing)


def _rule_based(score: int, matched: list, missing: list) -> str:
    lines = []
    lines.append("## Overall Assessment")
    if score >= 80:
        lines.append("Strong match for this role. Your profile aligns well with the job requirements. Apply with confidence.")
    elif score >= 60:
        lines.append("Good match overall. A few targeted improvements will make your application significantly stronger.")
    elif score >= 40:
        lines.append("Partial match. You have relevant skills but notable gaps exist. Focus on bridging these before applying.")
    else:
        lines.append("Low match for this specific role. Consider upskilling or targeting roles that better fit your profile.")

    lines.append("\n## Matched Skills")
    if matched:
        lines.append("✅ " + ", ".join(matched[:8]))
    else:
        lines.append("No direct skill matches found with this job description.")

    lines.append("\n## Missing Skills — Add These to Your Resume")
    if missing:
        for s in missing[:6]:
            lines.append(f"❌ {s}")
    else:
        lines.append("No critical missing skills detected.")

    lines.append("\n## Priority Action Items")
    lines.append("1. Add missing keywords from the job description to your resume")
    lines.append("2. Quantify your achievements instead of generic descriptions")
    lines.append("3. Deploy your projects online and add live URLs to your resume")

    return "\n".join(lines)