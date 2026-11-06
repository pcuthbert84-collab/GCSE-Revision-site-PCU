"""Small, offline-safe formative learning checks and route recommendations.

No automatic AI marks for learning checks. The learner sees an example answer
after they submit and self-reflects. Exam-practice marks remain provisional.
"""

def learning_checks(ai_guide=None, local_note=None):
    """Return up to two original/approved questions with reference explanations."""
    if isinstance(ai_guide,dict):
        raw=ai_guide.get("quick_check",[])
        if isinstance(raw,list):
            valid=[
                {"question":row["question"].strip(),"answer":row["answer"].strip()}
                for row in raw if isinstance(row,dict)
                and isinstance(row.get("question"),str)
                and isinstance(row.get("answer"),str)
                and row["question"].strip() and row["answer"].strip()
            ]
            if valid:
                return valid[:2]
    if isinstance(local_note,dict):
        questions=local_note.get("questions",[])
        if isinstance(questions,list):
            valid=[
                {"question":row["prompt"].strip(),"answer":row["model"].strip()}
                for row in questions if isinstance(row,dict)
                and isinstance(row.get("prompt"),str)
                and isinstance(row.get("model"),str)
                and row["prompt"].strip() and row["model"].strip()
            ]
            return valid[:2]
    return []

def suggested_route(mark, maximum, uncertain=False):
    """Recommend next learning action, never infer security from an uncertain mark."""
    if uncertain or not isinstance(mark,(int,float)) or not isinstance(maximum,(int,float)) or maximum<=0:
        return "review", "Your result is uncertain. Review the explanation, then retry a question."
    score=mark/maximum
    if score<0.5:
        return "learn", "Revisit the worked example and common misconceptions before another practice question."
    if score<0.8:
        return "improve", "Use the feedback to improve this answer, then try a new question at a similar level."
    return "challenge", "Good progress. Try another question at a higher level of challenge."
