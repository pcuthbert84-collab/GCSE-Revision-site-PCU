"""Conservative deterministic marking for exact mathematical answers.
Method marks cannot be safely inferred from arbitrary prose: no invented partial credit.
"""
import re
from sympy import simplify, sympify

SAFE_PATTERN = re.compile(r'^[\d\s,;./()+*^xX=+\-]+$')

def parse_numbers(text):
    """Only parse comma/semicolon-separated numeric answers, supporting fractions.
    Algebraic working belongs in the separate working field.
    """
    if not text or not SAFE_PATTERN.fullmatch(text):
        return []
    clean = re.sub(r'(?i)\bx\s*=\s*', '',text.replace('^','**'))
    parts = re.split(r'[,;\n]+|\s+or\s+',clean,flags=re.I)
    vals=[]
    for part in parts:
        part=part.strip()
        if not part:continue
        try:
            val = sympify(part, evaluate=True)
            if val.is_number and val.is_real and val.is_finite:
                vals.append(val)
            else:
                return []
        except Exception:
            return []
    return vals

def mark(question, final_answer, working=''):
    expected = question['answers']
    submitted = parse_numbers(final_answer)
    if not submitted:
        return {'correct':False,'mark':0,'max_mark':question['marks'],'feedback':'Enter the final numerical answer(s) in the requested format. Use commas to separate two values. Keep any method in the working box.','needs_review':False}
    if question['type']=='roots':
        correct=len(submitted)==2 and all(any(simplify(a-b)==0 for b in expected) for a in submitted) and len(set(map(str,submitted)))==2
    else:
        correct=len(submitted)==len(expected) and all(simplify(a-b)==0 for a,b in zip(submitted,expected))
    if correct:
        msg='Your final answer is correct. Compare your working with the model method after finishing.'
    else:
        msg='Your final answer is not fully correct yet. Check the method and your arithmetic. You can improve it before revealing the solution.'
    # Exact checking only: award full marks for a correct final answer as prototype score,
    # but warn it is not an exam-board method-mark assessment.
    return {'correct':correct,'mark':question['marks'] if correct else 0,'max_mark':question['marks'],
            'feedback':msg, 'needs_review': bool(working.strip()), 'method_note':'Prototype scores final-answer correctness only; working and method marks require a later reviewed marking engine.'}
