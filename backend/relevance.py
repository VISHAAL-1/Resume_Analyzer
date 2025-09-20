import json
from backend.utils.preprocessing import clean_text, extract_skills_from_text
from backend.utils.embeddings import similarity_between_texts
from rapidfuzz import fuzz

def hard_match_score(resume_text: str, must_have: list, good_to_have: list):
    resume = clean_text(resume_text)
    
    # Use extract_skills_from_text for a more robust check
    all_jd_skills = must_have + good_to_have
    found_skills = extract_skills_from_text(resume, extra_skills=all_jd_skills)
    
    matched_must = [s for s in must_have if s.lower() in [fs.lower() for fs in found_skills]]
    matched_good = [s for s in good_to_have if s.lower() in [fs.lower() for fs in found_skills]]

    must_pct = (len(matched_must) / max(1, len(must_have))) * 100
    good_pct = (len(matched_good) / max(1, len(good_to_have))) * 100 if good_to_have else 0
    
    hard = 0.7 * must_pct + 0.3 * good_pct
    
    missing_must = [s for s in must_have if s not in matched_must]
    
    return {
        "hard_score": round(hard, 2),
        "matched_must": matched_must,
        "matched_good": matched_good,
        "missing_must": missing_must
    }

def semantic_score(resume_text: str, job_text: str):
    try:
        sim = similarity_between_texts(resume_text, job_text)
        sim_pct = max(0.0, min(1.0, sim)) * 100
    except Exception as e:
        print(f"Semantic scoring failed: {e}")
        sim_pct = 0.0
    return round(sim_pct, 2)

def final_evaluate(resume_text: str, job_row):
    must = json.loads(job_row.must_have or "[]")
    good = json.loads(job_row.good_to_have or "[]")

    hard = hard_match_score(resume_text, must, good)

    jtxt = " ".join([job_row.title or ""] + must + good)
    sem = semantic_score(resume_text, jtxt)

    overall = round(0.6 * hard["hard_score"] + 0.4 * sem, 2)
    
    if overall > 75:
        verdict = "High"
    elif overall > 50:
        verdict = "Medium"
    else:
        verdict = "Low"

    feedback = []
    if len(hard["missing_must"]) > 0:
        feedback.append(f"Missing must-have skills: {', '.join(hard['missing_must'])}. Add projects/experience showing these.")
    else:
        feedback.append("All must-have skills present (or matched).")

    if sem < 40:
        feedback.append("Lacks semantic overlap with role; tailor resume summary and projects to the JD.")
    elif sem < 60:
        feedback.append("Some semantic overlap — consider emphasizing relevant projects/experiences.")
    else:
        feedback.append("Good semantic fit with job description.")

    return {
        "score": overall,
        "verdict": verdict,
        "hard_score": hard["hard_score"],
        "semantic_score": sem,
        "missing_skills": hard["missing_must"],
        "matched_must": hard["matched_must"],
        "matched_good": hard["matched_good"],
        "feedback": " ".join(feedback)
    }