# backend/utils/preprocessing.py
import re
import json
from rapidfuzz import fuzz

# Small skill list - extend as needed
COMMON_SKILLS = [
    "python","java","c++","c","sql","nosql","mongodb","postgresql","mysql",
    "aws","azure","gcp","docker","kubernetes","linux","git","tensorflow","pytorch",
    "scikit-learn","machine learning","deep learning","nlp","computer vision",
    "react","angular","node.js","javascript","html","css","excel","tableau","powerbi",
    "spark","hadoop","rest api","flask","fastapi","django","spring boot"
]

def clean_text(text: str) -> str:
    if not text:
        return ""
    s = text.replace("\n", " ").lower()
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def extract_skills_from_text(text: str, extra_skills: list = None, threshold: int = 85):
    """
    Return a list of skills found in text by checking COMMON_SKILLS + extra_skills.
    Uses substring match + fuzzy matching via rapidfuzz.
    """
    text_clean = clean_text(text)
    skill_bank = set(COMMON_SKILLS)
    if extra_skills:
        for s in extra_skills:
            skill_bank.add(s.lower())
    found = set()
    for skill in skill_bank:
        if skill in text_clean:
            found.add(skill)
        else:
            # fuzzy check (skill against sliding windows is heavy; we do a partial_ratio)
            score = fuzz.partial_ratio(skill, text_clean)
            if score >= threshold:
                found.add(skill)
    return sorted(found)