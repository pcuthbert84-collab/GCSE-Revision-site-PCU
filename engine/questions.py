"""Original, parameterised question templates. No third-party exam text is copied."""
from random import Random
from sympy import Symbol, expand, latex, Rational
from courses.maths_4ma1 import get_skill

x = Symbol('x')

def make_question(skill_id: str, difficulty: str = 'Standard', seed: int | None = None):
    """Create a fresh solvable question with known exact answers and marking guidance."""
    if not get_skill(skill_id) or not get_skill(skill_id)['enabled']:
        raise ValueError('Selected skill is not available in this prototype.')
    r = Random(seed)
    d = {'Foundation': 0, 'Standard': 1, 'Challenge': 2}.get(difficulty, 1)
    if skill_id == 'quadratic_factorise':
        a = r.choice([-7,-6,-5,-4,-3,2,3,4,5,6])
        b = r.choice([-6,-5,-4,-3,2,3,4,5,6,7])
        while a == b or (d == 0 and (abs(a) > 4 or abs(b)>4)):
            a,b = r.choice([-4,-3,-2,1,2,3,4]),r.choice([-4,-3,-2,1,2,3,4])
        poly = expand((x-a)*(x-b))
        return {'skill_id':skill_id,'difficulty':difficulty,'type':'roots','prompt':f'Solve the equation: $${latex(poly)} = 0$$ Give both values of $x$.',
                'answers':[a,b], 'marks':3, 'hint':'Can you find two numbers whose product is the constant term and whose sum is the coefficient of x?',
                'working':f'Factorise: $({latex(x-a)})({latex(x-b)})=0$. So $x={a}$ or $x={b}$.',
                'rubric':['Correct factorisation or equivalent method','One correct root','Both correct roots'], 'signature':f'factorise_{min(a,b)}_{max(a,b)}'}
    if skill_id == 'quadratic_formula':
        a,b = r.sample([-7,-6,-5,-4,-3,2,3,4,5,6,7],2)
        mult = 1 if d == 0 else r.choice([1,2,3])
        poly = expand(mult*(x-a)*(x-b))
        return {'skill_id':skill_id,'difficulty':difficulty,'type':'roots','prompt':f'Use the quadratic formula to solve: $${latex(poly)} = 0$$ Give both values of $x$.',
                'answers':[a,b], 'marks':4, 'hint':'Identify a, b and c, then substitute into the quadratic formula. Check the discriminant.',
                'working':f'Using $x=\\frac{{-b\\pm\\sqrt{{b^2-4ac}}}}{{2a}}$, the two values are $x={a}$ and $x={b}$.',
                'rubric':['Correct a, b and c','Substitution into quadratic formula','One correct root','Both correct roots'], 'signature':f'formula_{mult}_{min(a,b)}_{max(a,b)}'}
    if skill_id == 'percentage_change':
        original = r.choice([80,120,150,200,240,300,400,500])
        pct = r.choice([5,10,15,20,25,30])
        increase = r.choice([True,False])
        result = Rational(original*(100+pct if increase else 100-pct),100)
        action = 'increased' if increase else 'decreased'
        return {'skill_id':skill_id,'difficulty':difficulty,'type':'number','prompt':f'An item costs **{original} AED**. The price is {action} by **{pct}%**. Calculate the new price in AED.',
                'answers':[result], 'marks':3, 'hint':'Find the percentage change first, then add it to or subtract it from the original amount.',
                'working':f'{pct}% of {original} = {original*pct/100:g}. New price = {result} AED.',
                'rubric':['Find percentage amount','Apply correct increase/decrease','Correct final amount'], 'signature':f'pct_{original}_{pct}_{increase}'}
    if skill_id == 'ratio_share':
        aa,bb = r.randint(2,6),r.randint(2,7)
        unit = r.choice([5,10,15,20])
        total = (aa+bb)*unit
        return {'skill_id':skill_id,'difficulty':difficulty,'type':'pair','prompt':f'Share **{total} AED** between Ali and Sara in the ratio **{aa}:{bb}**. Enter both amounts, Ali first.',
                'answers':[aa*unit,bb*unit], 'marks':3, 'hint':'How many parts are there in total? What is the value of one part?',
                'working':f'{aa}+{bb}={aa+bb} parts. One part is {total}/{aa+bb}={unit}. Ali gets {aa*unit} AED and Sara gets {bb*unit} AED.',
                'rubric':['Find total parts','Find value of one part','Both allocations correct'], 'signature':f'ratio_{aa}_{bb}_{unit}'}
    raise ValueError('Unsupported skill')
