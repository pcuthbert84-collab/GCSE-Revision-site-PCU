"""Optional Gemini integration. Never submits student identifying data."""
import json
import os
import urllib.request
import urllib.error

class AIUnavailable(Exception):
    pass

def get_key():
    try:
        import streamlit as st
        return st.secrets.get('GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
    except Exception:
        return os.getenv('GEMINI_API_KEY','')

def get_model():
    try:
        import streamlit as st
        return st.secrets.get('GEMINI_MODEL','gemini-2.5-flash-lite')
    except Exception:
        return os.getenv('GEMINI_MODEL','gemini-2.5-flash-lite')

def request_json(instruction, payload):
    key=get_key()
    if not key:
        raise AIUnavailable('No Gemini API key configured. The free offline activity is available instead.')
    model=get_model()
    url=f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    body={'contents':[{'role':'user','parts':[{'text': instruction+'\nINPUT:\n'+json.dumps(payload,ensure_ascii=False)}]}],
          'generationConfig':{'temperature':0.35,'responseMimeType':'application/json'}}
    req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=32) as resp:
            data=json.load(resp)
        s=data['candidates'][0]['content']['parts'][0]['text']
        result=json.loads(s)
        if not isinstance(result,dict): raise ValueError('Expected object')
        return result
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,KeyError,IndexError) as e:
        raise AIUnavailable('AI could not return a valid response. You can continue with free offline practice.') from e

GENERATION_RULES="""You are an academically cautious UK school revision question writer.
Return one JSON object with exactly fields: prompt (plain student-facing question), hint (non-answer-leaking short hint),
model_answer (accurate example answer), marking_points (list of 2-5 assessable criteria), marks (integer 1-6).
Write an ORIGINAL, self-contained question. Do not quote or imitate specific published past-paper items.
Respect the supplied course and topic. Never claim an exam board/specification code unless verified flag true.
No external sources or citations. No references to a missing diagram, passage, recording, experiment results or text.
For a topic requiring a source stimulus or performance, create an honest low-stakes knowledge or planning task instead.
If the topic is too vague, write a concrete foundational knowledge question that is transparently practice, not a past-paper question.
Use valid mathematics and check the answer. No personal data. Output JSON only."""

FEEDBACK_RULES="""You are a supportive GCSE practice tutor. Return JSON fields:
strengths (string), improvement (string), tentative_mark (integer 0..maximum), confidence ('low'|'medium'|'high').
Assess ONLY the student's supplied answer against the supplied original model_answer and marking_points.
Evaluate mathematically equivalent expressions and valid alternative wording fairly.
Do not disclose the full model answer or answer points before second attempt.
For partial/incorrect answers give a specific constructive clue, not the answer.
No student identity. Scores are indicative, not examiner-awarded. Output JSON only."""

def generate(course,area,topic,tier='Higher',difficulty='Standard'):
    res=request_json(GENERATION_RULES,{'course':course['name'],'board':course.get('board'), 'code':course.get('code'),
           'verified':course.get('spec_verified',False),'area':area,'topic':topic,'tier':tier,'difficulty':difficulty})
    if not isinstance(res.get('prompt'),str) or not isinstance(res.get('model_answer'),str) or not isinstance(res.get('marking_points'),list):
        raise AIUnavailable('Question failed the basic structure check.')
    if not (1 <= int(res.get('marks',0)) <= 6) or len(res['marking_points'])<1:
        raise AIUnavailable('Question failed the marking criteria check.')
    if not isinstance(res.get('hint'),str) or len(res['prompt'])>2500:
        raise AIUnavailable('Question failed the content check.')
    return res

def feedback(question,answer):
    res=request_json(FEEDBACK_RULES,{'question':question['prompt'],'model_answer':question['model_answer'],
          'marking_points':question['marking_points'],'maximum':question['marks'],'student_answer':answer})
    mark=res.get('tentative_mark',0)
    if not isinstance(mark,int) or not 0<=mark<=question['marks'] or not isinstance(res.get('improvement'),str):
        raise AIUnavailable('The feedback could not be validated.')
    return res
