from engine.questions import make_question
from engine.marking import mark
from engine.progress import summaries, next_difficulty

def test_qa():
    for skill in ['quadratic_factorise','quadratic_formula','percentage_change','ratio_share']:
        for seed in range(50):
            q=make_question(skill,seed=seed)
            answer=', '.join(str(a) for a in q['answers'])
            assert mark(q,answer)['correct'],(skill,q)
            assert not mark(q,'99999999')['correct']

def test_adapt():
    assert next_difficulty('Standard',True,None,False)=='Challenge'
    assert next_difficulty('Challenge',False,False,True)=='Standard'

def test_mastery():
    a={'skill_id':'quadratic_factorise','timestamp':'2026-11-01','signature':'1','first_correct':True,'revealed':False,'second_correct':None}
    result=summaries([a]);assert result['quadratic_factorise']['status']=='Gathering evidence'
