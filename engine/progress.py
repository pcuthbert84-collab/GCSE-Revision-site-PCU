"""Prototype learning evidence held in session only. No personal data sent to AI."""
from collections import defaultdict
from datetime import datetime, timezone

def make_attempt(question, first, second=None, revealed=False):
    return {'timestamp':datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'skill_id':question['skill_id'], 'difficulty':question['difficulty'],
            'max_mark':question['marks'], 'first_correct':bool(first['correct']) if first else False,
            'second_correct':None if second is None else bool(second['correct']),
            'revealed':bool(revealed), 'signature':question['signature']}

def summaries(attempts):
    grouped=defaultdict(list)
    for a in attempts: grouped[a['skill_id']].append(a)
    result={}
    for skill,items in grouped.items():
        independent=sum(a['first_correct'] for a in items)
        coverage=len(items)
        score=independent/coverage if coverage else 0
        # A "secure" label requires >=3 independent correct across >=4 different questions,
        # and at least one separate-day attempt; until then show 'Gathering evidence'.
        distinct=len({a['signature'] for a in items})
        days=len({a['timestamp'][:10] for a in items})
        secure=(coverage>=4 and distinct>=4 and independent>=3 and score>=.8 and days>=2)
        if secure:status='Secure'
        elif coverage<3 or distinct<2:status='Gathering evidence'
        elif score<.5:status='Priority'
        else:status='Developing'
        result[skill]={'attempts':coverage,'first_accuracy':score,'status':status,'improved':sum(a['second_correct'] is True and not a['first_correct'] for a in items),'skipped':sum(a['revealed'] for a in items)}
    return result

def next_difficulty(current, first_correct, second_correct, revealed):
    levels=['Foundation','Standard','Challenge']
    i=levels.index(current)
    if revealed or (not first_correct and not second_correct):return levels[max(0,i-1)]
    if first_correct:return levels[min(2,i+1)]
    return current
