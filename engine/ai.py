"""Optional Gemini integration. Never submits student identifying data."""
import json
import os
import urllib.request
import urllib.error
import time

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

# A secondary model is useful for upstream 503 errors. Never use this to bypass
# 429 quotas, authentication failures, or paid-only model restrictions.
# Both defaults have published free-tier text API availability; a project's own
# billing settings are still the owner's responsibility.
FREE_FALLBACK_MODELS = {'gemini-3.1-flash-lite', 'gemini-3.5-flash-lite'}

def get_fallback_model():
    try:
        import streamlit as st
        name = st.secrets.get('GEMINI_FALLBACK_MODEL', 'gemini-3.1-flash-lite')
    except Exception:
        name = os.getenv('GEMINI_FALLBACK_MODEL', 'gemini-3.1-flash-lite')
    name = str(name).strip().removeprefix('models/')
    return name if name in FREE_FALLBACK_MODELS else ''

def _is_upstream_unavailable(error):
    msg = str(error)
    return any(x in msg for x in ('HTTP 500', 'HTTP 502', 'HTTP 503', 'HTTP 504', 'timed out'))

def _safe_api_message(status, raw):
    """Classify an upstream error without publishing credentials or user content."""
    try:
        doc=json.loads(raw)
        error=doc.get('error',{})
        code=error.get('status','')
    except (ValueError,TypeError,AttributeError):
        code=''
    guidance={
        400:'Invalid request. Check that the model supports structured JSON output.',
        401:'Authentication failed. Check the API key in Streamlit Secrets.',
        403:'Access denied. Check API key restrictions and Gemini API permissions.',
        404:'Model not found for this API key or API version. Run the model-list test below.',
        429:'Free-tier quota or rate limit reached. Check Google AI Studio usage.',
        500:'Gemini server error. Try again later.',
        502:'Gemini server error. Try again later.',
        503:'Gemini service temporarily unavailable. Try again later.',
        504:'Gemini request timed out. Try again later.',
    }
    return f'Gemini HTTP {status} ({code or "API error"}): '+guidance.get(status,'Request failed; check the Google AI Studio project and model.')


def _request(body, model, timeout=42):
    key=get_key()
    if not key:
        raise AIUnavailable('No Gemini API key configured in Streamlit Secrets.')
    url=f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    req=urllib.request.Request(url,data=json.dumps(body).encode('utf-8'),headers={'Content-Type':'application/json','x-goog-api-key':key},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=timeout) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        raw=e.read(4000).decode('utf-8','replace')
        raise AIUnavailable(_safe_api_message(e.code,raw)) from e
    except urllib.error.URLError as e:
        raise AIUnavailable('Unable to reach Gemini. Check network connectivity or API service availability.') from e
    except TimeoutError as e:
        raise AIUnavailable('Gemini timed out. Try a shorter question or try again.') from e
    except (ValueError,UnicodeError) as e:
        raise AIUnavailable('Gemini returned invalid HTTP JSON.') from e


def _extract_text(data):
    try:
        candidate=data['candidates'][0]
        chunks=[part.get('text','') for part in candidate.get('content',{}).get('parts',[]) if isinstance(part,dict)]
        combined='\n'.join(chunks).strip()
        if not combined:
            reason=candidate.get('finishReason','unknown')
            raise AIUnavailable(f'Gemini provided no text (finish reason: {reason}).')
        return combined
    except (KeyError,IndexError,TypeError) as e:
        raise AIUnavailable('Gemini returned no usable candidate; check its safety and output settings.') from e


def _parse_json_object(raw):
    """Accept proper JSON, or a JSON object surrounded by accidental markdown fences.

    Never use eval or try to invent missing values.
    """
    raw=raw.strip()
    try:
        obj=json.loads(raw)
    except (TypeError,ValueError):
        # Some models include a fenced object despite the JSON response MIME type.
        import re
        raw=re.sub(r'^```(?:json)?\s*', '', raw, flags=re.IGNORECASE)
        raw=re.sub(r'\s*```$', '', raw)
        try:
            obj=json.loads(raw)
        except (TypeError,ValueError) as e:
            raise AIUnavailable('Gemini returned invalid or truncated JSON. The generated guide was not displayed. Please retry.') from e
    if not isinstance(obj,dict):
        raise AIUnavailable('Gemini returned a JSON value instead of a guide object. Please retry.')
    return obj


def request_json(instruction, payload, max_output_tokens=8192):
    """Structured generation; on upstream 5xx only, try one other free-tier model.

    Do not change models on HTTP 429 or authentication/permission errors. Never
    use arbitrary models chosen by the AI or send credentials to the UI.
    """
    primary=get_model().strip().removeprefix('models/')
    backup=get_fallback_model()
    models=[primary]
    if backup and backup != primary:
        models.append(backup)
    body={'contents':[{'role':'user','parts':[{'text':instruction+'\nINPUT:\n'+json.dumps(payload,ensure_ascii=False)}]}],
          'generationConfig':{'temperature':0.2,'responseMimeType':'application/json',
                              'maxOutputTokens':max_output_tokens}}
    for i,model in enumerate(models):
        try:
            data=_request(body,model,timeout=65)
            candidate=(data.get('candidates') or [{}])[0]
            if candidate.get('finishReason','')=='MAX_TOKENS':
                raise AIUnavailable('Gemini stopped early (MAX_TOKENS). Use a shorter topic or compact guide.')
            return _parse_json_object(_extract_text(data))
        except AIUnavailable as exc:
            if i==0 and len(models)>1 and _is_upstream_unavailable(exc):
                # Only one attempt per model to protect free quotas.
                continue
            if i>0 and _is_upstream_unavailable(exc):
                raise AIUnavailable(
                    f'Both free-tier Gemini models failed with temporary upstream errors: '
                    f'{primary} and {model}. Google service capacity appears unavailable; '
                    'the problem is not your key or JSON parser. Offline revision remains available.'
                ) from exc
            raise
    raise AIUnavailable('Gemini could not complete this request.')


def connection_test(model_override=None):
    """Call the configured model with a tiny structured-output test; do not reveal the key."""
    model=(model_override or get_model()).strip()
    body={'contents':[{'parts':[{'text':'Return exactly this JSON object: {"status":"ok"}'}]}],
          'generationConfig':{'temperature':0,'responseMimeType':'application/json','maxOutputTokens':128}}
    result=_request(body,model,timeout=20)
    raw=_extract_text(result)
    try:
        content=json.loads(raw)
    except ValueError as e:
        raise AIUnavailable('Connection succeeded, but Gemini did not return JSON. Check the model response mode.') from e
    if content.get('status')!='ok':
        raise AIUnavailable('Connection succeeded but the JSON test answer was unexpected.')
    return f'Connected successfully to {model}. JSON output is working.'


def list_available_models():
    """Check whether this API key can see its requested Gemini model."""
    key=get_key()
    if not key:raise AIUnavailable('No Gemini API key configured.')
    req=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models?pageSize=100',headers={'x-goog-api-key':key})
    try:
        with urllib.request.urlopen(req,timeout=18) as resp:data=json.load(resp)
    except urllib.error.HTTPError as e:
        raise AIUnavailable(_safe_api_message(e.code,e.read(4000).decode('utf-8','replace'))) from e
    except (urllib.error.URLError,TimeoutError) as e:
        raise AIUnavailable('Could not connect to model catalogue.') from e
    target=get_model().strip().removeprefix('models/')
    matches=[m for m in data.get('models',[]) if m.get('name','').removeprefix('models/')==target]
    if matches:
        methods=matches[0].get('supportedGenerationMethods',[])
        return f'Model {target} is visible to this key. generateContent supported: {"generateContent" in methods}.'
    alternatives=[m['name'].removeprefix('models/') for m in data.get('models',[]) if 'generateContent' in m.get('supportedGenerationMethods',[]) and 'flash' in m.get('name','')]
    return f'Model {target} was NOT listed for this key. Available Flash models (first 8): '+', '.join(alternatives[:8])

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
