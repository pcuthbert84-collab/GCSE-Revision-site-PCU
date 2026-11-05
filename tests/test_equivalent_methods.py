from engine.questions import make_question
from engine.marking import mark, parse_numbers


def test_alternative_method_and_order_are_accepted():
    for skill in ('quadratic_factorise', 'quadratic_formula'):
        q = make_question(skill, seed=42)
        a, b = q['answers']
        for final in (f'x = {b}, x = {a}', f'{b} or {a}', f'{a}; {b}'):
            result = mark(q, final, 'I used a different valid technique.')
            assert result['correct'] is True, (skill, final, result)
            assert result['mark'] == q['marks']


def test_equivalent_fraction_answer():
    q = make_question('percentage_change', seed=1)
    a = q['answers'][0]
    assert mark(q, f'({2*a})/2')['correct'] is True


def test_ratio_must_preserve_order():
    q = make_question('ratio_share', seed=4)
    a, b = q['answers']
    assert mark(q, f'Ali: {a}, Sara: {b}')['correct'] is True
    if a != b:
        assert mark(q, f'{b}, {a}')['correct'] is False


def test_ambiguous_answer_not_falsely_marked_wrong():
    q = make_question('quadratic_factorise', seed=3)
    result = mark(q, 'I solved this in my working.', 'x^2 + ... = 0')
    assert result['correct'] is None
    assert result['mark'] is None


def test_sample_number_variants():
    assert parse_numbers('x = -2, x = 3') == [-2, 3]
    assert parse_numbers('−2 or 3') == [-2, 3]
    assert parse_numbers('Ali: 40 AED; Sara: 60 AED') == [40, 60]


def test_80_increased_by_20_percent_with_alternative_working():
    question = {'type':'number','answers':[96],'marks':3}
    working = '80 x 0.2 = 16\n80 + 16 = 96'
    for final, steps in [(working, ''), ('96', working), ('', working)]:
        result = mark(question, final, steps)
        assert result['correct'] is True, (final, steps, result)
        assert result['mark'] == 3

def test_invalid_arithmetic_steps_cannot_be_used_as_proof():
    question = {'type':'number','answers':[96],'marks':3}
    result = mark(question, '80 x 0.2 = 15\n80 + 15 = 96')
    assert result['correct'] is None
    assert result['needs_review'] is True
