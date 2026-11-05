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
        return {
            'correct': None, 'mark': None, 'max_mark': question['marks'],
            'feedback': ('I cannot reliably read your final answer. This is **not a wrong mark**. '
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
    return {
        'correct': correct, 'mark': question['marks'] if correct else 0,
        'max_mark': question['marks'], 'feedback': feedback,
        'needs_review': bool(working.strip()) and not correct,
        'method_note': ('Final-answer accuracy only. Working has not been reliably awarded method marks. '
                        'If your method is valid but the answer checker is unsure, request review.')
    }
