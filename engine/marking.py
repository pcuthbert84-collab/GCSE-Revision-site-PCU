"""Conservative, mathematically aware marking for the initial 4MA1 skills.

Final-answer equality is independent of the method used.  Never award or deduct
method marks based on a mismatch to the displayed worked example.  Ambiguous
working is left ungraded rather than labelled incorrect.
"""
import re
from sympy import simplify, sympify

# Only allow a small whitelist of arithmetic syntax; no arbitrary SymPy functions.
NUMBER_TOKEN = re.compile(r'^[\d\s.()+*/^\-]+$')
PREFIX = re.compile(r'^(?:x\s*=\s*|(?:ali|sara)\s*[:=]\s*)', re.I)


def _numeric(fragment):
    fragment = PREFIX.sub('', fragment.strip()).strip().replace('^', '**')
    # A money or percent unit is not part of an arithmetic expression.
    fragment = re.sub(r'\s*(?:AED|د\.إ)\s*$', '', fragment, flags=re.I).strip()
    if not fragment or len(fragment) > 90 or not NUMBER_TOKEN.fullmatch(fragment):
        return None
    try:
        value = sympify(fragment, evaluate=True)
        if value.is_number and value.is_real and value.is_finite:
            return value
    except (TypeError, ValueError, SyntaxError, ZeroDivisionError, AttributeError):
        return None
    return None


def parse_numbers(text):
    """Understand variants: x=2, x=-3; -3 or 2; Ali: 40, Sara: 60.

    This parser deliberately does not mine random numbers from explanatory
    prose or intermediate working: those are not necessarily final answers.
    """
    if not text or len(text) > 500:
        return []
    clean = text.strip().replace('−', '-').replace('×', '*').replace('÷', '/')
    clean = clean.replace('，', ',')
    clean = re.sub(r'\b(?:and|or)\b', ',', clean, flags=re.I)
    parts = re.split(r'[,;\n]+', clean)
    values = []
    for part in parts:
        if not part.strip():
            continue
        value = _numeric(part)
        if value is None:
            return []
        values.append(value)
    return values


def _arithmetic_steps(text):
    """Read complete, valid numeric equations such as '80 x 0.2 = 16'.

    Only recognise arithmetic, not arbitrary symbolic or prose reasoning.
    Return (last right-hand value, all_equations_valid), or (None, False).
    """
    if not text or len(text) > 700:
        return None, False
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return None, False
    # A standalone final numeric value may follow the working.
    if '=' not in lines[-1]:
        last = _numeric(lines[-1])
    else:
        last = None
    equations = []
    for line in lines:
        # 'x' between numbers denotes multiplication, not the variable x.
        clean = line.replace('×', '*').replace('÷', '/').replace('−', '-')
        clean = re.sub(r'(?<=\d)\s*[xX]\s*(?=\d)', '*', clean)
        if '=' not in clean:
            if _numeric(clean) is None:
                return None, False
            continue
        pieces = [segment.strip() for segment in clean.split('=')]
        if len(pieces) < 2:
            return None, False
        nums = [_numeric(segment) for segment in pieces]
        if any(n is None for n in nums):
            return None, False
        if any(simplify(a - b) != 0 for a, b in zip(nums, nums[1:])):
            return None, False
        equations.append(nums[-1])
    if not equations and last is None:
        return None, False
    return last if last is not None else equations[-1], True


def _matches(expected, submitted, qtype):
    if len(submitted) != len(expected):
        return False
    if qtype == 'roots':
        # Distinct roots are an unordered set; the exemplar root order is irrelevant.
        return all(any(simplify(s-e)==0 for s in submitted) for e in expected) and all(
            any(simplify(e-s)==0 for e in expected) for s in submitted
        )
    return all(simplify(s-e)==0 for s,e in zip(submitted, expected))



def _verified_method_credit(question, response):
    """Very conservative partial credit for known, original numeric templates.

    Recognises only meaningful correct intermediate calculations. This is a
    *practice estimate*, not an attempt to reproduce Pearson's official rubric.
    """
    sid=question.get('skill_id')
    if sid not in ('percentage_change','ratio_share'):
        return 0, ''
    lines=[line.strip() for line in response.splitlines() if '=' in line]
    verified=[]
    for line in lines:
        clean=line.replace('×','*').replace('÷','/').replace('−','-')
        clean=re.sub(r'(?<=\d)\s*[xX]\s*(?=\d)','*',clean)
        parts=[_numeric(p.strip()) for p in clean.split('=')]
        if len(parts)>=2 and all(p is not None for p in parts) and all(simplify(a-b)==0 for a,b in zip(parts,parts[1:])):
            verified.append(parts[-1])
    if not verified:return 0,''
    parts=question.get('signature','').split('_')
    try:
        if sid=='percentage_change' and len(parts)==4:
            original,pct=int(parts[1]),int(parts[2])
            expected_change=sympify(original*pct)/100
            if any(simplify(v-expected_change)==0 for v in verified):
                return 1,'Correctly calculated the percentage amount (one provisional method mark).'
        elif sid=='ratio_share' and len(parts)==4:
            aa,bb,unit=map(int,parts[1:4])
            if any(simplify(v-(aa+bb))==0 for v in verified):
                return 1,'Correctly found the total number of ratio parts (one provisional method mark).'
            if any(simplify(v-unit)==0 for v in verified):
                return 1,'Correctly found the value of one ratio part (one provisional method mark).'
    except (ValueError,TypeError):pass
    return 0,''


def mark(question, final_answer, working=''):
    """Return correct / incorrect / review-needed with transparent scope.

    A mathematically correct final answer gets full *prototype answer-check*
    credit, regardless of how the student derived it.  This is NOT a claim
    about formal Pearson method marks.  Unknown or absent answers are not
    asserted incorrect.  Working never has to match the model method.
    """
    expected = question['answers']
    submitted = parse_numbers(final_answer)
    interpreted_steps = False
    # Some students reasonably type their working AND answer together.
    # Only infer the final answer for single-number questions when every
    # arithmetic equality is mathematically true.
    if question['type'] == 'number' and not submitted:
        candidate, valid = _arithmetic_steps(final_answer)
        if valid:
            submitted = [candidate]
            interpreted_steps = True
    if question['type'] == 'number' and not submitted and working.strip():
        candidate, valid = _arithmetic_steps(working)
        if valid:
            submitted = [candidate]
            interpreted_steps = True
    if not submitted:
        method_credit,method_message=_verified_method_credit(question,final_answer+'\n'+working)
        return {
            'correct': None, 'mark': method_credit or None, 'max_mark': question['marks'],
            'feedback': (method_message+' ' if method_credit else '') + ('I cannot reliably read your final answer. This is **not a wrong mark**. '
                         'Please enter the final value(s) separately (for example `x = -2, x = 3`). '
                         'Your working may use any valid method.'),
            'needs_review': True,
            'method_note': 'Working has not been marked or compared with a model method.'
        }
    correct = _matches(expected, submitted, question['type'])
    if correct:
        feedback = ('✅ **Correct final answer.** Your method does not need to match the example. '
                    'Alternative valid working is accepted; the example is only one possible approach.')
        if interpreted_steps:
            feedback += ' I also checked the arithmetic equalities in the steps you entered.'
    else:
        feedback = ('Your final answer does not match the verified solution yet. '
                    'Check your arithmetic and final values. **This is not a judgement that your method is wrong.** '
                    'You can revise your answer or reveal the worked solution.')
    method_credit,method_message=_verified_method_credit(question,final_answer+'\n'+working) if not correct else (0,'')
    if method_credit:feedback+=' '+method_message+' This is not a complete examiner mark.'
    return {
        'correct': correct, 'mark': question['marks'] if correct else method_credit,
        'max_mark': question['marks'], 'feedback': feedback,
        'needs_review': bool(working.strip()) and not correct,
        'method_note': ('Maths final answers are checked exactly; only narrow, verified numerical steps receive provisional credit. '
                        'If your method is valid but the answer checker is unsure, request review.')
    }
