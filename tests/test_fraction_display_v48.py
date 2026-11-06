from engine.math_display import stacked_fractions
from engine.v4_ai import QUESTION_RULES, STUDY_RULES, FEEDBACK_RULES


def test_algebraic_fraction_is_stacked():
    assert stacked_fractions('Simplify (x+1)/(2x-3).') == 'Simplify $\\dfrac{x+1}{2x-3}$.'


def test_simple_fractions_are_stacked():
    assert stacked_fractions('x/2 and 3/4') == '$\\dfrac{x}{2}$ and $\\dfrac{3}{4}$'


def test_math_delimiters_stay_single():
    assert stacked_fractions('Calculate $x/2$ and $$3/4$$') == 'Calculate $\\dfrac{x}{2}$ and $$\\dfrac{3}{4}$$'


def test_existing_fraction_latex_is_not_corrupted():
    text=r'Find $\dfrac{x+1}{2x-3}$.'
    assert stacked_fractions(text) == text


def test_urls_dates_code_not_corrupted():
    text='https://school.org/topic/1/2 and 11/06/2026 and `x/2`'
    assert stacked_fractions(text) == text


def test_math_instruction_is_in_all_generation_and_marking_prompts():
    for rule in (QUESTION_RULES, STUDY_RULES, FEEDBACK_RULES):
        assert r'\dfrac{numerator}{denominator}' in rule
