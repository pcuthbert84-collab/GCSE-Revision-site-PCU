"""On-demand AI: structured original teaching and questions. No API calls until user action."""
from engine.ai import request_json, AIUnavailable
import re

def safe_source(text):
    """Only a short topic description, never the full internal school file."""
    text=re.sub(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b','[redacted]', text or '')
    text=re.sub(r'\b\+?\d[\d ()-]{8,}\b','[redacted]', text)
    return re.sub(r'\s+',' ',text)[:350]

def _payload(course,topic,area,tier,difficulty):
    return dict(subject=course['name'],qualification=course.get('kind'),board=course.get('board'),
         code=course.get('code'),curriculum_confirmation='DBSJP school map; official micro-specification not independently checked',
         theme=area,topic=topic['title'],school_context=safe_source(topic.get('source','')),
         tier=tier,difficulty=difficulty)

STUDY_RULES='''You are preparing school revision notes, not quoting an awarding body. Create an accurate and genuinely useful ORIGINAL tutorial for the precise topic supplied. If the topic contains several skills, focus on the explicit headline and state what is covered. Do not guess set-text quotations, legal facts, historical dates, exact specifications or unseen stimuli; omit unsupported details. Never claim a school/internal source or an official specification proves your explanation. Specific mathematical examples must be checked by working backwards. For languages, provide target-language examples and translations. For BTEC coursework, focus on concepts and skills, never invent an actual assessed assignment. For a practical arts topic, explain a legitimate technique and clear evidence of a successful outcome. Return ONLY JSON object with: title (str), outcomes (array of 2-4 measurable strings), explanation (3-6 sentences of substantive subject-specific teaching, not generic advice), key_points (array of 4-7 detailed accurate teaching points), worked_example (concrete stepwise example including verified answer when possible), pitfalls (array of 2-4 precise common mistakes), quick_check (array of 3 pairs {question,answer}), uncertainty (str, leave blank if none). Avoid exam-board copyright text. Students are approximately 14-16 years old.'''
QUESTION_RULES='''Write ONE original high-quality GCSE/Level-2 practice item for the specific subject, topic, tier and difficulty. Do not copy or paraphrase a published past-paper question. The task must be self-contained, with all necessary numerical data, source extracts (original only), units and assumptions. Avoid dependence on unseen images, poetry, literature quotations, websites, plays, fieldwork reports or unseen primary sources. Prefer an authentic subject task to generic recall. For maths and science, independently verify computations and show a correct worked solution. For history or geography where factual detail may be uncertain, pose precise skills-based tasks rather than invent facts. Marking points must be distinct and add up to max_marks, with each having credit (integer) and criterion (string). A valid alternative approach earns equivalent credit; method marks should not require the exact example. For writing/creative subjects, provide transparent AO-like criteria but do not promise official-grade equivalence. For coursework BTEC, use a standalone skill exercise, not an actual assignment. Answer must NOT appear in the question stem or hint. Return JSON ONLY: {prompt:string, question_type:string, hint:string, model_answer:string, max_marks:integer 2..8, marking_points:[{criterion:string,credit:integer}], reference_method:string, uncertainty:string}. Student response may be multiple lines of working.''' 
FEEDBACK_RULES='''You are providing formative, provisional practice feedback, not official examiner assessment. Review the ORIGINAL question, rubric, and the learner's complete answer including any calculations. Accept mathematically equivalent answers, exact fractions, reordered roots, and any sound alternative method. Never insist student work matches the exemplar. Check whether final answers and steps are valid. Do not infer missing reasoning. Award supported partial marks only where evidence exists, but if uncertain flag needs_review rather than penalising. Explain a specific strength and an actionable clue WITHOUT revealing complete model answer at first feedback. Do not say incorrect merely because you cannot parse the format. Return JSON ONLY: {indicative_mark:integer, strength:string, next_step:string, correct_independently:boolean, needs_review:boolean, confidence:string (low/medium/high), reason:string}. Ensure 0<=mark<=maximum.'''

COMPACT_STUDY_RULES='''Produce a concise but substantive original Year 10/11 revision lesson on this exact school topic. No generic study tips or invented course requirements. Respond with a single JSON object using EXACTLY these keys: title (string), outcomes (array with 2 short items), explanation (string, 90-170 words with subject-specific explanation), key_points (array of 4 detailed facts/techniques), worked_example (string, one accurate concrete example with steps), pitfalls (array of 2 concrete misconceptions), quick_check (array of 2 objects each with question and answer strings), uncertainty (string, empty if none). Make responses compact. Never reproduce exam-board questions or invent quotations.'''

def _study_validation(r):
    if not isinstance(r,dict):return 'Gemini returned an invalid study-guide structure.'
    text_fields=('title','explanation','worked_example')
    missing=[k for k in text_fields if not isinstance(r.get(k),str) or not r[k].strip()]
    list_fields=('outcomes','key_points','pitfalls','quick_check')
    missing += [k for k in list_fields if not isinstance(r.get(k),list) or len(r[k])<2]
    if missing:
        return 'Gemini guide is missing required sections: '+', '.join(missing)+'.'
    if not all(isinstance(x,dict) and isinstance(x.get('question'),str) and isinstance(x.get('answer'),str) for x in r['quick_check']):
        return 'Gemini quick-check questions were malformed.'
    if len(r['explanation'])<100:return 'Gemini explanation was too short to teach this topic.'
    return None

def create_study(course,topic,area,tier='Higher',difficulty='Standard'):
    payload=_payload(course,topic,area,tier,difficulty)
    # First try a compact guide: less prone to output truncation, lower token usage.
    # Only retry with a still smaller prompt if required fields are missing.
    r=request_json(COMPACT_STUDY_RULES,payload,max_output_tokens=6144)
    err=_study_validation(r)
    if err:
        # Keep a useful diagnostic rather than silently swallowing response errors.
        raise AIUnavailable(err+' Use the AI guide diagnostic to troubleshoot.')
    r.setdefault('uncertainty','')
    return r

def create_question(course,topic,area,tier='Higher',difficulty='Standard'):
    r=request_json(QUESTION_RULES,_payload(course,topic,area,tier,difficulty))
    required=['prompt','model_answer','hint','reference_method']
    if not all(isinstance(r.get(k),str) and len(r[k])>8 for k in required):raise AIUnavailable('Question was incomplete.')
    try:points=r['marking_points'];maximum=int(r['max_marks'])
    except (KeyError,TypeError,ValueError):raise AIUnavailable('Question rubric was incomplete.')
    if not 2<=maximum<=8 or not isinstance(points,list) or not points or any(not isinstance(p,dict) or not isinstance(p.get('criterion'),str) or not isinstance(p.get('credit'),int) or p['credit']<1 for p in points) or sum(p['credit'] for p in points)!=maximum:
        raise AIUnavailable('Question marks do not add up; please generate another question.')
    if len(r['prompt'])>3000 or len(r['model_answer'])>3500:raise AIUnavailable('Question format exceeded limits.')
    return r

def evaluate(q,answer,second=False):
    r=request_json(FEEDBACK_RULES,dict(question=q['prompt'],max_marks=q['max_marks'],marking_points=q['marking_points'],
      reference_solution=q['model_answer'],student_work=answer,attempt='second' if second else 'first'))
    if not isinstance(r.get('indicative_mark'),int) or not 0<=r['indicative_mark']<=q['max_marks'] or not all(isinstance(r.get(k),str) for k in ['strength','next_step','confidence']):
        raise AIUnavailable('Feedback could not be validated; no mark was given.')
    if r.get('confidence') not in ('low','medium','high'):r['confidence']='low'
    if r.get('confidence')=='low':r['needs_review']=True
    return r
