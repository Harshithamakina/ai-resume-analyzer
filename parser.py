import re
import pdfplumber
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError("Run: python -m spacy download en_core_web_sm")

SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "golang", "ruby", "php",
    "react", "angular", "vue", "html", "css", "tailwind",
    "django", "fastapi", "flask", "spring boot", "express",
    "postgresql", "mysql", "mongodb", "redis", "sqlite", "firebase",
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux",
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "langchain", "openai", "llm", "rag",
    "rest api", "graphql", "celery", "n8n", "airflow", "kafka",
    "pytest", "selenium", "postman", "figma", "power bi", "tableau",
    "streamlit", "huggingface", "faiss", "spacy", "nltk",
}

def extract_text(pdf_file) -> str:
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()

def extract_name(text: str) -> str:
    doc = nlp(text[:500])
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
            return ent.text.strip()
    for line in text.split("\n"):
        line = line.strip()
        if line and 3 < len(line) < 50 and line.replace(" ", "").isalpha():
            return line
    return "Not found"

def extract_email(text: str) -> str:
    m = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return m.group(0) if m else "Not found"

def extract_phone(text: str) -> str:
    m = re.search(r'(\+91[\-\s]?)?[6-9]\d{9}|(\+\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}', text)
    return m.group(0).strip() if m else "Not found"

def extract_linkedin(text: str) -> str:
    m = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
    return "https://" + m.group(0) if m else "Not found"

def extract_github(text: str) -> str:
    m = re.search(r'github\.com/[\w\-]+', text, re.IGNORECASE)
    return "https://" + m.group(0) if m else "Not found"

def extract_skills(text: str) -> list:
    text_lower = text.lower()
    found = []
    for skill in SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill.title())
    return sorted(found)

def extract_education(text: str) -> list:
    edu_kw = ["b.tech", "b.e", "m.tech", "mca", "bca", "b.sc", "m.sc",
              "mba", "ph.d", "diploma", "bachelor", "master", "degree",
              "university", "college", "institute", "jntu", "anna university"]
    results = []
    for line in text.split("\n"):
        if any(kw in line.lower() for kw in edu_kw):
            clean = line.strip()
            if clean and len(clean) > 5:
                results.append(clean)
    return results[:4]

def extract_experience_years(text: str) -> float:
    patterns = [
        r'(\d+\.?\d*)\+?\s*years?\s*of\s*(professional\s*)?experience',
        r'experience[:\s]+(\d+\.?\d*)\s*years?',
        r'(\d+\.?\d*)\s*years?\s*(of\s*)?(work\s*)?experience',
    ]
    for p in patterns:
        m = re.search(p, text.lower())
        if m:
            return float(m.group(1))
    return 0.0

def parse_resume(pdf_file) -> dict:
    text = extract_text(pdf_file)
    return {
        "raw_text": text,
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "github": extract_github(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience_years": extract_experience_years(text),
    }
