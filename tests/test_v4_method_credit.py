from engine.questions import make_question
from engine.marking import mark

def test_percent_partial_method_credit():
    q=make_question('percentage_change',seed=3)
    parts=q['signature'].split('_')
    original,pct=int(parts[1]),int(parts[2])
    value=original*pct/100
    # An accurate percentage calculation but wrong final value gets some
    # provisional method credit, not a forced zero.
    answer=f'{original} x {pct/100} = {value:g}\nFinal answer: -999'
    r=mark(q,answer)
    assert r['mark']>=1 and r['mark']<r['max_mark']

def test_irrelevant_equation_does_not_get_method_credit():
    q=make_question('percentage_change',seed=3)
    r=mark(q,'2+2=4\n999')
    assert r['mark']==0
