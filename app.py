"""DBSJP Revision Hub V4.10: content-first subject practice with optional free-tier Gemini.
No student accounts, progress database, permanent question bank or paid endpoints.
"""
import secrets
import json
import streamlit as st
from courses.v4_catalog import COURSES, topic_groups
from courses.revision_content import get_content
from courses.maths_4ma1 import SKILLS
from engine.questions import make_question
from engine.marking import mark
from engine.ai import get_key, get_model, get_fallback_model, connection_test, list_available_models, AIUnavailable
from engine.v4_ai import create_study,create_question,create_exam_question,evaluate
from engine.exam_modes import exam_modes
from engine.quality_store import (load as quality_load, save as quality_save, configured as quality_configured,
    password_valid, approve_rule, add_resource, active_rules, archive, validate_direct_url)
from courses.verified_resources import topic_resources
from courses.subject_resource_atlas import qualification_reference,directory_resources,topic_references,SEPARATE_SCIENCE_SPECS
from courses.corbett_catalogue import fetch_catalogue, automatic_resources, candidate_matches, resources_for_entry, normalize
from engine.math_display import stacked_fractions
from engine.learning_path import learning_checks, suggested_route

st.set_page_config(page_title='DBSJP Revision Hub | V4.15',page_icon='📚',layout='wide')
st.markdown('''<style>
.block-container{max-width:1090px;padding-top:1.8rem;padding-bottom:3rem}
[data-testid="stSidebar"]{min-width:260px}
h1,h2,h3{letter-spacing:-.02em}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px}
:root{--dbsjp-navy:#071D59;--dbsjp-red:#D50032;--dbsjp-light:#F4F6FA}
h1,h2,h3{color:var(--dbsjp-navy);font-weight:700}
[data-testid="stSidebar"]{background:var(--dbsjp-navy)}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,
[data-testid="stSidebar"] small{color:#fff!important}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{opacity:.88}
[data-testid="stSidebar"] [role="radiogroup"] label{border-radius:9px}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#152B6B}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.23)}
[data-testid="stSidebar"] .dbsjp-brand{background:#fff;border-radius:12px;padding:12px;margin:0 0 15px}
[data-testid="stSidebar"] .dbsjp-brand .dbsjp-brand-copy strong,
[data-testid="stSidebar"] .dbsjp-brand .dbsjp-brand-copy span,
[data-testid="stSidebar"] .dbsjp-brand .dbsjp-brand-copy small{color:var(--dbsjp-navy)!important}
[data-testid="stButton"] button[kind="primary"]{background:var(--dbsjp-red);border-color:var(--dbsjp-red);color:#fff;font-weight:650}
[data-testid="stButton"] button[kind="primary"]:hover{background:#AD0028;border-color:#AD0028;color:#fff}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:#dce3ef}
a{color:#0C357C}
.dbsjp-brand{display:flex;align-items:center;gap:12px;padding:4px 0 18px}
.dbsjp-brand-logo{width:62px;height:62px;object-fit:contain;background:#fff;border-radius:9px;padding:3px;flex-shrink:0}
.dbsjp-brand-copy{display:flex;flex-direction:column;line-height:1.18}
.dbsjp-brand-copy strong{font-size:1.1rem;color:inherit;letter-spacing:.025em}
.dbsjp-brand-copy span{font-size:1.0rem;font-weight:600}
.dbsjp-brand-copy small{font-size:.72rem;margin-top:5px;opacity:.8}
</style>''',unsafe_allow_html=True)

# Limits are session-level safeguards only. Provider-side free-tier quota / no paid billing
# must be configured independently; shared persistent quota enforcement is out of scope.
MAX_AI_CALLS_PER_SESSION=65
for name,default in {'ai_calls':0,'notes_cache':{},'active_question':None,'attempt_stage':'new',
                     'first_text':'','retry_text':'','first_result':None,'second_result':None,
                     'attempt_summary':[],'reported_issues':[],'question_key':None,'level':'Standard','start_id':0,'admin_authorised':False,'learning_revealed':{}}.items():
    if name not in st.session_state:st.session_state[name]=default

def can_ai():return bool(get_key()) and st.session_state.ai_calls<MAX_AI_CALLS_PER_SESSION

def with_ai(func,*args,**kwargs):
    if not can_ai():raise AIUnavailable('Gemini key missing or this browser session has reached its AI-call safety cap.')
    st.session_state.ai_calls+=1
    return func(*args,**kwargs)

def read_quality():
    try:
        data,sha,durable=quality_load()
        return data,sha,durable
    except (RuntimeError,ValueError,KeyError) as exc:
        st.warning('Approved quality data is temporarily unavailable: '+str(exc))
        return {'rules':[], 'resources':[], 'audit':[]},None,False


def context_rules(course,topic):
    data,_,_=read_quality()
    return active_rules(data,course['name'],topic['title'])


@st.cache_data(ttl=86400, show_spinner=False)
def live_corbett_catalogue():
    """Fetch the real published index at most daily per Streamlit cache."""
    return fetch_catalogue()

def try_corbett_catalogue():
    try: return live_corbett_catalogue(), ''
    except Exception as exc: return [], str(exc)


def show_resources(course,topic):
    st.divider()
    st.markdown('#### Free resources for this exact topic')
    data,_,_=read_quality()
    items=topic_resources(data,course['name'],topic['title'])
    if course['name']=='Mathematics':
        index_rows,_=try_corbett_catalogue()
        items += automatic_resources(index_rows,course['name'],topic['title'])
        items=list({item['url']:item for item in items}.values())
    if not items:
        st.info('No direct resource link has been verified for this exact topic yet. We will not show a generic homepage or invented link. An administrator can approve one in Academic Quality Manager.')
        return
    for item in items:
        st.link_button(item['title'],item['url'])
        st.caption(item.get('provider','Approved provider')+' · direct topic resource, not necessarily written for this exact examination board')
    with st.expander('Report an incorrect or broken revision link'):
        link_note=st.text_area('Which link is wrong, and why?',key='resource_issue_'+str(abs(hash((course['name'],topic['title'])))))
        if st.button('Add resource issue to review list',disabled=not link_note.strip(),key='report_resource_'+str(abs(hash((course['name'],topic['title']))))):
            st.session_state.reported_issues.append({'subject':course['name'],'topic':topic['title'],'question':'Resource links: '+', '.join(item['url'] for item in items),'issue':link_note,'question_source':'revision link','first_feedback':''})
            st.success('Resource issue added to Testing issues for administrator review.')


def show_subject_library(course,topic,area=''):
    """Exact learning pages first; optional directories and specifications below."""
    official=qualification_reference(course)
    related=topic_references(course['name'],topic['title'],topic.get('source',''),area)
    directories=directory_resources(course['name'])
    # Prevent duplicate buttons when a direct topic page is also an index hit.
    seen=set()
    related=[item for item in related
             if not (item['url'] in seen or seen.add(item['url']))]
    direct=[item for item in related if item.get('kind')=='direct_topic']
    other=[item for item in related if item.get('kind')!='direct_topic']
    if direct:
        st.markdown('#### Matched topic lessons and practice')
        st.caption('Matched to this precise topic. Check provider content against your DBSJP lesson and tier.')
        for item in direct:
            st.link_button(item['title'],item['url'])
            st.caption(item['note'])
    else:
        st.caption('No individually verified external lesson has been matched to this exact title yet. '
                   'Try choosing a narrower skill, or use the resource collections below.')
    with st.expander('Official specification and wider revision collections'):
        st.caption('External resources may be copyrighted, subscription-based or written for a different '
                   'UK GCSE route. A general directory is not a verified match to your exact syllabus point.')
        if official:
            st.link_button(official['title'],official['url'])
            st.caption('Official qualification overview, not confirmation of the school-selected unit, option or tier.')
        elif course['name']=='Separate Sciences':
            st.info('AQA Separate Sciences have three independent specifications and tiers.')
            for reference in SEPARATE_SCIENCE_SPECS:
                st.link_button(reference['title'],reference['url'])
        else:
            st.caption('No independently checked specification link for this exact qualification code.')
        if other:
            st.markdown('**Relevant specification sections and topic indexes**')
            for item in other:
                st.link_button(item['title'],item['url'])
                st.caption(item['note'])
        if directories:
            st.markdown('**General subject revision collections**')
            for item in directories:
                st.link_button(item['title'],item['url'])
                st.caption(item['note'])
    options=([official] if official else [])+related+directories
    if options:
        with st.expander('Report a broken, incorrect or misleading external link'):
            choices={str(i)+'. '+item['title']:item for i,item in enumerate(options,1)}
            selection=st.selectbox('Resource to report',list(choices),
                key='atlas_report_pick_'+str(abs(hash((course['name'],topic['title'])))))
            issue=st.text_area('What needs correcting?',max_chars=700,
                placeholder='For example: this link is for a different qualification or no longer works.',
                key='atlas_report_note_'+str(abs(hash((course['name'],topic['title'])))))
            if st.button('Add resource report for academic review',
                         disabled=not issue.strip(),
                         key='atlas_report_submit_'+str(abs(hash((course['name'],topic['title']))))):
                item=choices[selection]
                st.session_state.reported_issues.append({
                    'subject':course['name'],'topic':topic['title'],
                    'question':'External resource: '+item['title']+' '+item['url'],
                    'issue':issue.strip(),'question_source':'subject_resource_atlas',
                    'first_feedback':''})
                st.success('Report saved in this browser session. Export it from Testing issues.')



def reset_q():
    for k,v in {'active_question':None,'attempt_stage':'new','first_text':'','retry_text':'',
                'first_result':None,'second_result':None,'question_key':None}.items():st.session_state[k]=v

def local_math_skills(topic):
    # Existing exact-solution templates from V3.2.
    names={'quadratic_factorise':'Quadratic factorisation','quadratic_formula':'Quadratic formula',
           'percentage_change':'Percentage increase/decrease','ratio_share':'Sharing in a ratio'}
    return [(item['id'],names[item['id']]) for row in SKILLS.values() for item in row if item.get('enabled')]

def same_topic_local(name,title):
    t=title.lower()
    if name!='Mathematics':return None
    for needle,sid in [('quadratic formula','quadratic_formula'),('quadratic equation','quadratic_factorise'),('factoris','quadratic_factorise'),
                       ('percentage','percentage_change'),('ratio','ratio_share')]:
        if needle in t:return sid
    return None

def local_notes_for(name,title):
    if title.startswith('Y10') or title.startswith('Y11'):return None
    return get_content(name,title)

def switch_route(route):
    """Called by Streamlit buttons before widgets are instantiated on rerun."""
    st.session_state.revision_route=route


def render_learning_checks(course, area, topic, tier, guide=None, local_note=None):
    """Formative retrieval checks; never award unsound numerical marks."""
    checks=learning_checks(guide,local_note)
    if not checks:
        st.info('When a revision guide or reviewed local lesson is available, short learning checks will appear here.')
        return
    st.markdown('#### Check your understanding')
    st.caption('Try each question from memory. Reveal the reference answer only after writing your own response. These are learning checks, not examination marks.')
    identity=(course['name'],area,topic['title'],tier)
    for i,check in enumerate(checks):
        item_key='lc_'+str(abs(hash(identity+(i,))))
        st.markdown('**Check '+str(i+1)+':** '+stacked_fractions(check['question']))
        attempt=st.text_area('Your answer',key=item_key+'_answer',height=90,
            placeholder='Write what you remember before viewing the example answer.')
        reveal_key=item_key+'_revealed'
        if st.button('Reveal reference answer',key=item_key+'_reveal',disabled=not attempt.strip()):
            st.session_state.learning_revealed[reveal_key]=True
        if st.session_state.learning_revealed.get(reveal_key):
            st.markdown('**Example answer:** '+stacked_fractions(check['answer']))
            reflection=st.radio('How close was your response?',
                ['Not yet secure','Partly correct','Secure'],
                key=item_key+'_reflection',horizontal=True)
            if reflection=='Not yet secure':
                st.info('Revisit the worked example, then try explaining this idea again without looking.')
            elif reflection=='Partly correct':
                st.info('Identify the key detail you missed and add it to your own answer.')
            else:
                st.success('Ready to try exam practice on this topic.')
    st.button('Continue to exam practice',type='primary',
        key='move_to_exam',on_click=switch_route,args=('Exam practice',))


def render_notes(note):
    st.markdown('#### Learning outcomes')
    for p in note['outcomes']:st.markdown('- '+stacked_fractions(str(p)))
    st.markdown('#### Understand the topic')
    st.markdown(stacked_fractions(note['explanation']))
    st.markdown('#### Essential knowledge')
    for p in note['key_points']:st.markdown('- '+stacked_fractions(str(p)))
    st.markdown('#### Worked example')
    st.markdown(stacked_fractions(note['worked_example']))
    st.markdown('#### Common mistakes')
    for p in note['pitfalls']:st.markdown('- '+stacked_fractions(str(p)))
    st.caption('Retrieval questions appear below. Try them before revealing the example answers.')
    if note.get('uncertainty'):st.warning('Content to check: '+note['uncertainty'])
    st.caption('AI-created revision explanation; not approved or written by the examination board. Please report any inaccuracies.')

def revise(course,area,topic,tier):
    st.subheader('Revise · '+topic['title'])
    cached_key=(course['name'],area,topic['title'],tier)
    old=local_notes_for(course['name'],topic['title'])
    if cached_key in st.session_state.notes_cache:
        render_notes(st.session_state.notes_cache[cached_key])
    elif old:
        st.markdown('#### What you need to know');st.markdown(stacked_fractions(old['goal']))
        st.markdown('#### Essential knowledge')
        for p in old['points']:st.markdown('- '+stacked_fractions(p))
        st.markdown('**Worked explanation:** '+stacked_fractions(old['example']))
        st.markdown('**Common mistake:** '+stacked_fractions(old['mistake']))
        if can_ai() and st.button('Create a more detailed revision guide',key='upgrade_notes'):
            try:
                with st.spinner('Preparing a topic-specific explanation…'):
                    st.session_state.notes_cache[cached_key]=with_ai(create_study,course,topic,area,tier,rules=context_rules(course,topic))
                st.rerun()
            except AIUnavailable as ex:st.warning(str(ex))
    else:
        if topic['kind']=='school':
            with st.expander('What DBSJP teaches in this block',expanded=True):
                st.write(topic['source'][:1600])
                st.caption('Extracted from '+topic['file']+'. This is a curriculum map, not a finished revision guide.')
        if can_ai():
            st.write('Generate a detailed, original explanation with key facts, worked examples and common mistakes for this selected topic.')
            if st.button('Generate revision guide',type='primary',key='create_notes'):
                try:
                    with st.spinner('Preparing a revision explanation…'):
                        st.session_state.notes_cache[cached_key]=with_ai(create_study,course,topic,area,tier,rules=context_rules(course,topic))
                    st.rerun()
                except AIUnavailable as ex:st.warning(str(ex))
        else:
            st.warning('A full explanation for this topic is not prewritten. Add the free Gemini API key in Streamlit Secrets to generate it, or use the original school course outline above.')
    render_learning_checks(course,area,topic,tier,
        guide=st.session_state.notes_cache.get(cached_key),local_note=old)
    show_resources(course,topic)
    with st.expander('Report an inaccurate revision explanation'):
        guide_note=st.text_area('What should be corrected?',key='guide_issue_'+str(abs(hash((course['name'],topic['title'])))))
        if st.button('Add revision issue to review list',disabled=not guide_note.strip(),key='report_guide_'+str(abs(hash((course['name'],topic['title']))))):
            st.session_state.reported_issues.append({'subject':course['name'],'topic':topic['title'],
                  'question':'Revision guide: '+topic['title'],'issue':guide_note,'question_source':'revision notes','first_feedback':''})
            st.success('Revision issue added to Testing issues for administrator review.')

def make_local_question(course,topic,difficulty):
    sid=same_topic_local(course['name'],topic['title'])
    if sid:
        q=make_question(sid,difficulty,seed=secrets.randbits(50))
        return {'kind':'exact','data':q,'prompt':q['prompt'],'max_marks':q['marks']}
    note=local_notes_for(course['name'],topic['title'])
    if note and note.get('questions'):
        idx=st.session_state.start_id%len(note['questions'])
        q=note['questions'][idx]
        return {'kind':'guided','data':q,'prompt':q['prompt'],'max_marks':len(q.get('points',[]))}
    return None

def new_question(course,area,topic,tier,difficulty,mode=None):
    # Extended tasks must not silently degrade into a short question.
    if mode and mode.get('id')!='short':
        if not can_ai():
            st.warning('Extended examination practice requires a configured Gemini key and available session quota.')
            return None
        try:
            with st.spinner('Creating and validating an original examination-style task…'):
                q=with_ai(create_exam_question,course,topic,area,mode,tier,difficulty,
                    rules=context_rules(course,topic))
            return {'kind':'ai','data':{**q,'_subject':course['name'],
                '_topic':topic['title']},'prompt':q['prompt'],'max_marks':q['max_marks']}
        except AIUnavailable as ex:
            st.warning('Extended question was not produced: '+str(ex))
            return None
    local=make_local_question(course,topic,difficulty)
    if can_ai():
        try:
            with st.spinner('Creating and checking a new question…'):
                q=with_ai(create_question,course,topic,area,tier,difficulty,rules=context_rules(course,topic))
            return {'kind':'ai','data':{**q,'_subject':course['name'],'_topic':topic['title']},'prompt':q['prompt'],'max_marks':q['max_marks']}
        except AIUnavailable as ex:
            if local:st.warning(str(ex)+' Using a local practice question instead.')
            else:st.warning(str(ex))
    return local

def assess_question(q,answer,second=False):
    if q['kind']=='exact':
        res=mark(q['data'],answer,'')
        return {'mark':res['mark'],'max':q['max_marks'],'correct':res['correct'], 'uncertain':res['correct'] is None,
                'strength':'The final-answer checker accepts different mathematically equivalent forms.' if res['correct'] else '',
                'next':res['feedback'],'confidence':'high' if res['correct'] is not None else 'low'}
    if q['kind']=='guided':
        return {'mark':None,'max':q['max_marks'],'correct':None,'uncertain':True,
                'strength':'Your response has been saved in this session.','next':'Compare your work with the success criteria after your second attempt. Automatic marking is unavailable in offline mode.','confidence':'low'}
    if can_ai():
        try:
            with st.spinner('Checking the answer and looking for valid alternative approaches…'):
                res=with_ai(evaluate,q['data'],answer,second=second,rules=active_rules(read_quality()[0],q['data'].get('_subject',''),q['data'].get('_topic','')))
            return {'mark':res['indicative_mark'],'max':q['max_marks'],
                    'correct':res.get('correct_independently'),'uncertain':bool(res.get('needs_review')),
                    'strength':res.get('strength',''), 'next':res['next_step'], 'confidence':res['confidence']}
        except AIUnavailable as ex: return {'mark':None,'max':q['max_marks'],'correct':None,'uncertain':True,'strength':'','next':str(ex),'confidence':'low'}
    return {'mark':None,'max':q['max_marks'],'correct':None,'uncertain':True,'strength':'','next':'AI feedback is unavailable at the moment. No incorrect mark is recorded.','confidence':'low'}

def render_feedback(res,first=True):
    if res is None:return
    if res['uncertain']:
        st.warning('Unable to verify confidently; not marked wrong.')
    elif res['correct'] is True and res.get('confidence')=='high':
        st.success('Correct answer or sufficiently supported solution.')
    else:st.info('Formative feedback')
    if res['mark'] is not None and (not res['uncertain'] or res['mark']>0):
        st.markdown(f"**{'Indicative mark' if res['confidence']!='high' else 'Checked/indicative mark'}:** {res['mark']}/{res['max']}")
    if res['strength']:st.markdown('**What went well:** '+stacked_fractions(res['strength']))
    if res['next']:st.markdown('**Next step:** '+stacked_fractions(res['next']))
    if first:st.caption('Feedback should help you improve without revealing the full solution. Marks on extended responses are provisional.')

def solution(q):
    st.markdown('#### Model answer and criteria')
    if q['kind']=='exact':
        st.markdown(stacked_fractions(q['data']['working']))
        for item in q['data'].get('rubric',[]):st.markdown('- '+stacked_fractions(item))
        st.caption('Exemplar method only. Other correct mathematical methods must also earn credit.')
    elif q['kind']=='guided':
        st.markdown(stacked_fractions(q['data']['model']))
        for item in q['data'].get('points',[]):st.markdown('- '+stacked_fractions(item))
    else:
        st.markdown(stacked_fractions(q['data']['model_answer']))
        for item in q['data']['marking_points']:
            st.markdown(f"- **{item['credit']} mark(s):** {stacked_fractions(item['criterion'])}")
        if q['data'].get('uncertainty'):st.warning('Check: '+q['data']['uncertainty'])
    st.caption('This is an original learning example, not an official past-paper mark scheme.')

def testing(course,area,topic,tier):
    st.subheader('Exam practice · '+topic['title'])
    context=(course['name'],area,topic['title'],tier)
    if st.session_state.question_key and st.session_state.question_key[:4]!=context:reset_q()
    if st.session_state.active_question is None:
        modes=exam_modes(course,area,topic)
        chosen_id=st.selectbox('Question format',[m['id'] for m in modes],
            format_func=lambda x:next(m['label'] for m in modes if m['id']==x),
            key='exam_format_selector')
        chosen_mode=next(m for m in modes if m['id']==chosen_id)
        st.caption(chosen_mode['description'])
        difficulty=st.select_slider('Difficulty',['Foundation','Standard','Challenge'],value=st.session_state.level,key='question_difficulty')
        st.write('Practise an original, examination-style task at a chosen difficulty. Submit a full answer, receive provisional feedback, and improve it on a second attempt.')
        st.caption('Practice questions are original. Extended-writing marks and criteria are indicative, not official examiner judgements.')
        if not can_ai():st.caption('AI is currently unavailable or has reached this session’s cap. Prewritten questions will be offered where available.')
        if st.button('Generate a question',type='primary'):
            q=new_question(course,area,topic,tier,difficulty,mode=chosen_mode)
            if q:
                st.session_state.active_question=q;st.session_state.question_key=context+(difficulty,)
                st.session_state.attempt_stage='first';st.rerun()
            else:
                if can_ai():
                    st.info('No reviewed offline question exists for this topic. Gemini was unable to create a complete question this time; the connection is configured. Try again or choose another topic.')
                elif get_key():
                    st.info('This browser session has reached its AI-request safety cap. There is no reviewed offline question for this topic.')
                else:
                    st.warning('No reviewed offline question exists for this topic. Configure the Gemini API key in Streamlit Secrets to generate questions.')
        return
    q=st.session_state.active_question
    st.caption(f"Original practice · {st.session_state.question_key[-1]} · {q['max_marks']} marks · {('AI-generated, provisional' if q['kind']=='ai' else 'Locally generated')}")
    st.markdown(stacked_fractions(q['prompt']))
    if q['kind']=='ai' and q['data'].get('practice_note'):
        st.info(q['data']['practice_note']+' Marks are provisional and require teacher moderation.')
    if st.session_state.attempt_stage=='first':
        st.text_area('Your full answer and working',key='first_text',height=180,placeholder='Show your method and your final answer. Alternative correct methods are welcome.')
        if st.button('Check my answer',type='primary',disabled=not st.session_state.first_text.strip()):
            st.session_state.first_result=assess_question(q,st.session_state.first_text)
            st.session_state.attempt_stage='feedback';st.rerun()
    elif st.session_state.attempt_stage=='feedback':
        render_feedback(st.session_state.first_result)
        if st.session_state.first_result.get('correct') is True and not st.session_state.first_result['uncertain']:
            st.success('You can finish now or try another question. You do not need to copy the model method.')
        with st.expander('Hint (optional)'):
            st.markdown(stacked_fractions(q['data'].get('hint','Review the question carefully.')))
        st.markdown('#### Improve your answer (optional)')
        st.text_area('Your second attempt',key='retry_text',height=170,placeholder='Improve your answer using the feedback above.')
        col1,col2=st.columns(2)
        with col1:
            if st.button('Submit second attempt',type='primary',disabled=not st.session_state.retry_text.strip()):
                st.session_state.second_result=assess_question(q,st.session_state.retry_text,second=True)
                st.session_state.attempt_stage='done';st.rerun()
        with col2:
            if st.button('Show solution / skip second attempt'):
                st.session_state.attempt_stage='done';st.rerun()
    else:
        if st.session_state.second_result:render_feedback(st.session_state.second_result,first=False)
        solution(q)
        f=st.session_state.first_result
        if f is not None and f['mark'] is not None and not f['uncertain']:
            if f['mark']>=0.8*f['max']:
                st.session_state.level={'Foundation':'Standard','Standard':'Challenge','Challenge':'Challenge'}[st.session_state.question_key[-1]]
            elif f['mark']<0.5*f['max']:
                st.session_state.level={'Foundation':'Foundation','Standard':'Foundation','Challenge':'Standard'}[st.session_state.question_key[-1]]
        st.caption('Next question difficulty is adjusted using first-attempt evidence, not hints or second-attempt marks.')
        _route,_tip=suggested_route(f.get('mark') if f else None,
            f.get('max') if f else None, bool(f.get('uncertain')) if f else True)
        st.info('Suggested next step: '+_tip)
        if _route in ('learn','review'):
            st.button('Return to the lesson for this topic',
                on_click=switch_route,args=('Learn the topic',),key='review_lesson')
        if st.button('Next question',type='primary'):
            st.session_state.start_id+=1;reset_q();st.session_state.question_difficulty=st.session_state.level;st.rerun()
    with st.expander('Flag a problem with this question or marking'):
        report_note=st.text_area('What should we check?',key='issue_note',placeholder='For example: my method was mathematically valid, but was marked wrong.')
        if st.button('Add to testing report',disabled=not report_note.strip()):
            st.session_state.reported_issues.append({'subject':course['name'],'topic':topic['title'],
              'question':q['prompt'],'issue':report_note,'question_source':q['kind'],
              'first_feedback':str((st.session_state.first_result or {}).get('next',''))})
            st.success('Added to this browser session’s testing report. Download it from the sidebar before leaving.')
    if st.button('Change topic / start over',key='clear_now'):
        reset_q();st.rerun()

def academic_quality_manager():
    st.title('Academic Quality Manager')
    st.write('Approve permanent subject-specific marking and content rules, and exact-topic revision links. Changes go to the private GitHub repository when configured; students cannot edit these rules.')
    if not quality_configured():
        st.warning('Permanent saving is NOT configured. Add QUALITY_GITHUB_REPO, QUALITY_GITHUB_TOKEN and QUALITY_ADMIN_PASSWORD to Streamlit Secrets. No web-admin changes can be saved until then.')
        st.info('The direct resource links bundled with V4.6 are still available without setup.')
        return
    if not st.session_state.admin_authorised:
        with st.form('admin_login'):
            candidate=st.text_input('Administrator password',type='password')
            login=st.form_submit_button('Unlock academic review')
        if login:
            if password_valid(candidate):
                st.session_state.admin_authorised=True;st.rerun()
            else:st.error('Incorrect password.')
        return
    if st.button('Lock Academic Quality Manager'):
        st.session_state.admin_authorised=False;st.rerun()
    try:
        data,sha,durable=quality_load()
    except (RuntimeError,ValueError) as exc:
        st.error('Unable to read quality data: '+str(exc));return
    if not durable:
        st.error('This is a preview. Permanent GitHub-backed storage is not active.');return
    st.success(f"Permanent review storage connected · {sum(r.get('status')=='approved' for r in data['rules'])} rules · {sum(r.get('status')=='approved' for r in data['resources'])} approved direct links")
    tab_rules,tab_links,tab_corbett,tab_items=st.tabs(['Approve correction','Approve exact-topic link','Corbettmaths catalogue','Review / archive'])
    with tab_rules:
        issue_options=st.session_state.reported_issues
        picked=None
        if issue_options:
            idx=st.selectbox('Optional tester report',[-1]+list(range(len(issue_options))),
              format_func=lambda n: 'No report selected' if n==-1 else issue_options[n]['subject']+' · '+issue_options[n]['topic']+' · '+issue_options[n]['issue'][:60])
            if idx!=-1:picked=issue_options[idx]
        subject_choices=sorted(COURSES)
        suggested_subject=(picked or {}).get('subject','Mathematics')
        with st.form('approve_rule'):
            scope=st.radio('Scope of approved correction',['topic','subject','all'],horizontal=True,
                help='Topic rules affect only the exact topic label. Subject rules affect the whole subject.')
            subject=st.selectbox('Subject',subject_choices,index=subject_choices.index(suggested_subject) if suggested_subject in subject_choices else 0)
            topic=st.text_input('Exact topic label',value=(picked or {}).get('topic',''),help='Copy the exact topic title shown in Revise & Test for a topic-only rule.')
            correction=st.text_area('Correct academic rule (review before approving)',height=140,
                  placeholder='For percentage increases, accept both a multiplier method and finding the increase separately. Check each valid arithmetic step.')
            example=st.text_area('Optional anonymised test example',height=90, value=(picked or {}).get('issue',''))
            confirmed=st.checkbox('I have checked that this rule is academically correct and appropriately scoped.')
            submit=st.form_submit_button('Approve and save permanent rule',type='primary')
        if submit:
            if not confirmed:st.error('Academic verification is required before approval.')
            else:
                try:
                    revised=approve_rule(data,scope=scope,subject=subject,topic=topic,correction=correction,example=example)
                    quality_save(revised,sha,action='approve rule');st.session_state.notes_cache={};reset_q();st.success('Rule permanently committed to GitHub. It will apply to later AI revision, questions and feedback.');st.rerun()
                except (RuntimeError,ValueError) as exc:st.error(str(exc))
    with tab_links:
        with st.form('approve_resource'):
            subject=st.selectbox('Subject',sorted(COURSES),key='link_subject')
            topic=st.text_input('Exact topic label',key='link_topic',help='Must match the selected topic exactly, including spelling.')
            title=st.text_input('Specific page or video title')
            provider=st.text_input('Provider',placeholder='Corbettmaths, Oak National Academy, ...')
            url=st.text_input('Direct HTTPS resource link',placeholder='https://provider.example/lesson/specific-topic')
            note=st.text_area('Reviewer verification: explain the exact subject/topic match and free access')
            verified=st.checkbox('I opened the exact link, checked it teaches this topic accurately, and confirmed free access for our testers.')
            submit=st.form_submit_button('Approve and permanently save direct link',type='primary')
        if submit:
            if not verified:st.error('You must personally verify the linked page before approving.')
            else:
                try:
                    revised=add_resource(data,subject=subject,topic=topic,title=title,url=url,provider=provider,reviewer_note=note)
                    quality_save(revised,sha,action='approve direct resource');st.success('Verified exact-topic link saved to GitHub.');st.rerun()
                except (RuntimeError,ValueError) as exc:st.error(str(exc))
        st.caption('The system checks the URL format and approved provider, but cannot guarantee that a webpage stays accessible or accurate. Check links manually before approval.')
    with tab_corbett:
        st.markdown('#### Corbettmaths: indexed video, questions and textbook exercise')
        st.caption('Live index from https://corbettmaths.com/contents/ (cached for 24 hours). Direct URLs are read from publisher links, never guessed from video numbers.')
        if st.button('Refresh Corbettmaths index from website'):
            live_corbett_catalogue.clear()
        entries,error=try_corbett_catalogue()
        if error:
            st.warning('Could not retrieve the published Corbettmaths catalogue. No new links are being recommended: '+error)
        else:
            st.success(f'{len(entries)} published rows found. Only exact title matches are shown automatically to students; other suggestions require approval.')
            math_groups=topic_groups('Mathematics')
            all_topics=[t for group in math_groups.values() for t in group]
            matches={t['title']:candidate_matches(entries,t['title'],t.get('source','')) for t in all_topics}
            exact_count=sum(bool([r for r in entries if r['key']==normalize(t['title'])]) for t in all_topics)
            suggested_count=sum(bool(matches[t['title']]) for t in all_topics)
            st.caption(f'DBSJP Maths selections: {len(all_topics)} · exact-title matches: {exact_count} · selections with review suggestions: {suggested_count}. Broad teaching blocks may contain several skills; these are never auto-approved.')
            choices=list(range(len(all_topics)))
            selected=st.selectbox('DBSJP Maths topic / teaching block',choices,
                  format_func=lambda i:all_topics[i]['title']+' · '+ ('school curriculum' if all_topics[i].get('source') else 'course index'))
            active=all_topics[selected]
            if active.get('source'):
                with st.expander('DBSJP curriculum context'):
                    st.write(active['source'])
            options=matches[active['title']]
            if not options:
                st.info('No matching publisher entries were found for this curriculum selection. You can still add an exact verified link using the other approval tab.')
            else:
                st.caption(f'{len(options)} possible publisher entries, including matches to individual curriculum-map lines.')
                labels=[f"{item['entry']['title']} (Video {item['entry']['video_number']}) — {item['match']}" for item in options]
                preview=st.selectbox('Preview and verify a proposed Corbettmaths entry',list(range(len(options))),format_func=lambda i:labels[i])
                preview_entry=options[preview]['entry']
                preview_links=resources_for_entry(preview_entry,active['title'])
                for resource in preview_links:
                    st.link_button('Open '+resource['title'],resource['url'])
                with st.form('approve_corbett_bundles'):
                    picks=st.multiselect('Select the exact Corbettmaths entries that genuinely teach this topic',list(range(len(options))),format_func=lambda i:labels[i])
                    for idx in picks[:10]:
                        row=options[idx]['entry']
                        st.markdown('**'+row['title']+'**')
                        for typ in ('video','practice','textbook'):
                            if row.get(typ):st.write(typ.title()+': '+row[typ])
                    reviewer_note=st.text_area('Verification notes',placeholder='I opened each selected lesson, checked the DBSJP topic and confirmed that the video/questions/exercise are appropriate and accessible.')
                    verified=st.checkbox('I opened and checked each selected resource and approve all its displayed links for this exact DBSJP topic.')
                    approved=st.form_submit_button('Approve selected resources and save permanently',type='primary')
                if approved:
                    if not picks:st.error('Select at least one publisher entry.')
                    elif not verified:st.error('Please personally check the exact resource pages before approving.')
                    elif len(reviewer_note.strip())<15:st.error('Include meaningful verification notes.')
                    else:
                        try:
                            updated=data
                            added=0
                            for idx in picks:
                                for resource in resources_for_entry(options[idx]['entry'],active['title']):
                                    if any(x.get('subject')=='Mathematics' and x.get('topic')==active['title'] and x.get('url')==resource['url'] and x.get('status')=='approved' for x in updated['resources']):
                                        continue
                                    updated=add_resource(updated,subject='Mathematics',topic=active['title'],title=resource['title'],url=resource['url'],provider='Corbettmaths',reviewer_note=reviewer_note)
                                    added+=1
                            if added:
                                quality_save(updated,sha,action='approve Corbettmaths index resources')
                                st.success(f'{added} direct resource links permanently saved to GitHub.');st.rerun()
                            else:st.info('All selected links are already approved for this topic.')
                        except (RuntimeError,ValueError) as exc:st.error(str(exc))

    with tab_items:
        for kind in ('rules','resources'):
            st.markdown('#### '+('Approved academic rules' if kind=='rules' else 'Approved topic resources'))
            for item in data[kind]:
                if item.get('status')!='approved':continue
                with st.expander(item.get('subject','All subjects')+' · '+item.get('topic','All topics')+' · '+item['id']):
                    st.write(item.get('instruction') or item.get('title'))
                    if item.get('url'):st.link_button('Check approved page',item['url'])
                    if st.button('Archive this item',key='archive_'+item['id']):
                        try:
                            updated=archive(data,item['id']);quality_save(updated,sha,action='archive approved item');st.success('Archived permanently.');st.rerun()
                        except (RuntimeError,ValueError) as exc:st.error(str(exc))
        st.download_button('Export approved quality data for ChatGPT improvements',
                           data=json.dumps(data,ensure_ascii=False,indent=2),
                           file_name='dbsjp_approved_academic_quality.json',mime='application/json')
        st.caption('For major code or marking-engine improvements, export this file and describe the issue in ChatGPT. Approved routine rules already persist across redeployments.')


def main():
    with st.sidebar:
        st.markdown('''<div class="dbsjp-brand" aria-label="Dubai British School Jumeirah Park">
  <img class="dbsjp-brand-logo" src="https://dubailocal.ae/assets/logo/1682999938_b3e76ff53712956525cc.png"
       alt="Dubai British School Jumeirah Park emblem" loading="eager"
       onerror="this.style.display='none'">
  <div class="dbsjp-brand-copy"><strong>DBSJP</strong><span>Revision Hub</span>
  <small>Enjoy · Aspire · Achieve</small></div>
</div>''',unsafe_allow_html=True)
        page=st.radio('Navigation',['Revise & Test','Academic Quality Manager','AI connection test','Official past papers','Testing issues','How this prototype works'])
        st.divider()
        st.caption('V4.15 • DBSJP • Specification-linked resources')
        st.caption('No accounts or stored progress')
        st.caption(('Gemini key configured (not yet verified)' if get_key() else 'Gemini not configured')+f' · {st.session_state.ai_calls}/{MAX_AI_CALLS_PER_SESSION} session calls')
        if get_key():st.caption('Each new AI guide, question or marking attempt uses the shared API project’s free allowance.')
    if page=='Academic Quality Manager':
        academic_quality_manager()
        return
    if page=='AI connection test':
        st.title('Gemini connection diagnostics')
        st.write('This test uses your configured key without displaying it. It makes one small Gemini request and may count towards your free quota.')
        st.info('Primary model: '+get_model()+' · Backup (temporary 5xx only): '+(get_fallback_model() or 'disabled'))
        if not get_key():
            st.error('GEMINI_API_KEY is missing from Streamlit Secrets.')
        else:
            if st.button('1. Check model availability'):
                try:
                    with st.spinner('Checking Google model catalogue…'):
                        st.success(list_available_models())
                except AIUnavailable as ex:st.error(str(ex))
            if st.button('2. Test model and JSON response'):
                try:
                    with st.spinner('Making a small structured-output request…'):
                        st.success(connection_test())
                except AIUnavailable as ex:st.error(str(ex))
            if st.button('2b. Test the backup model and JSON response'):
                backup=get_fallback_model()
                if not backup or backup==get_model().strip():
                    st.warning('No distinct approved backup model configured. Set GEMINI_FALLBACK_MODEL to gemini-3.1-flash-lite in Secrets.')
                else:
                    try:
                        with st.spinner('Testing alternate model without exposing your key…'):
                            st.success(connection_test(model_override=backup))
                    except AIUnavailable as ex:st.error(str(ex))
            st.divider()
            st.write('**3. Test a real revision-guide response**')
            st.caption('This tests the same generation and validation used by Revise, on a small, original BTEC Business topic. It uses your AI quota. No API key or student information is displayed.')
            if st.button('4. Test compact revision guide (lower output)'):
                try:
                    demo_course={'name':'BTEC Business Level 2','kind':'BTEC','board':'Pearson','code':'HBGY2'}
                    demo_topic={'title':'Teams and team-leading','source':'Team roles, leadership approaches, motivation and communication in businesses.'}
                    with st.spinner('Testing a shorter Gemini revision guide…'):
                        guide=with_ai(create_study,demo_course,demo_topic,'Business skills','Not tiered',compact=True)
                    st.success('Compact guide generated and validated.')
                    render_notes(guide)
                except AIUnavailable as ex:
                    st.error('Compact guide failed: '+str(ex))
                    st.info('This is an upstream AI service issue if it reports HTTP 503. It is not a JSON parsing problem.')
            if st.button('3. Test complete revision guide'):
                try:
                    demo_course={'name':'BTEC Business Level 2','kind':'BTEC','board':'Pearson','code':'HBGY2'}
                    demo_topic={'title':'Teams and team-leading','source':'Team roles, leadership approaches, motivation and communication in businesses.'}
                    with st.spinner('Checking complete study-guide generation…'):
                        guide=with_ai(create_study,demo_course,demo_topic,'Business skills','Not tiered')
                    st.success('A complete topic-specific revision guide was generated and passed structural validation.')
                    render_notes(guide)
                except AIUnavailable as ex:
                    st.error('Revision guide generation failed: '+str(ex))
                    st.info('The small JSON test can pass while larger study-guide requests fail. This message identifies which stage failed.')
        st.caption('You can share the status message, HTTP code and model name. Never share your API key, Secrets screenshot or full request logs.')
        return
    if page=='Testing issues':
        st.title('Content and marking issues')
        st.write('Review student/tester reports. They remain in this browser session until exported or converted to a reviewed, approved rule by the administrator.')
        if st.session_state.reported_issues:
            for item in st.session_state.reported_issues:
                with st.expander(item['subject']+' · '+item['topic']):
                    st.write(item['issue']);st.caption(item['question'])
            st.download_button('Download testing report (JSON)',
                data=json.dumps(st.session_state.reported_issues,ensure_ascii=False,indent=2),
                file_name='dbsjp_v4_testing_issues.json',mime='application/json')
        else:st.info('No issues flagged yet. Use “Flag a problem” beside a question.')
        return
    if page=='How this prototype works':
        st.title('Version 4: scope and limitations')
        st.write('This release covers DBSJP Level 2 subjects, verified direct resource links, original AI questions, second attempts and indicative feedback. No student accounts or progress database are used. Approved corrections are stored in a private GitHub repository only when configured.')
        st.info('Mathematics: four existing skills have SymPy-verified exact answers; the rest use provisional AI marking. Extended writing, practical performance and coursework cannot be marked as reliably as a human examiner.')
        st.warning('Free-tier usage is shared across visitors. Session limits are a courtesy, not a global usage cap. Keep paid billing off in the AI project. Do not enter student names or identifying personal data.')
        st.write('Unverified micro-specification mapping is labelled. School teaching sequence does not itself establish exact examination-board coverage. Revision notes generated on demand must be checked.')
        return
    if page=='Official past papers':
        st.title('Genuine past-paper practice')
        st.write('Use the official examination board’s public past-paper collections. We do not copy protected questions or pass examination-board papers into AI without permission.')
        st.link_button('Pearson Edexcel qualifications','https://qualifications.pearson.com/en/qualifications.html')
        st.link_button('AQA qualifications','https://www.aqa.org.uk/subjects')
        return
    st.title('Choose your subject')
    subject=st.selectbox('Subject',sorted(COURSES),key='subject_choice')
    course=COURSES[subject]
    st.caption(f"{course.get('kind','Level 2')} · {course.get('board') or 'Board to confirm'} · {course.get('code') or 'Code to confirm'}")
    if course.get('note'):st.caption(course['note'])
    groupmap=topic_groups(subject)
    area=st.selectbox('Choose a topic group',list(groupmap),key=f'group_{subject}')
    topics=groupmap[area]
    # The authored school curriculum items are used as searchable topic context, not as copied specification statements.
    selection=st.selectbox('Choose a topic',list(range(len(topics))),format_func=lambda i:topics[i]['title'],key=f'skill_{subject}_{area}')
    topic=dict(topics[selection])
    if topic['kind']=='school':
        # Allow students to choose a narrower curriculum skill rather than ask AI
        # to assess a whole half-term containing many unrelated subtopics.
        raw_lines=[line.strip(' •-\t') for line in topic['source'].splitlines()]
        candidates=[]
        for line in raw_lines:
            if 4<=len(line)<=95 and sum(ch.isalpha() for ch in line)>=4 and line not in candidates:
                candidates.append(line)
        if len(candidates)>1:
            focus=st.selectbox('Focus on a specific skill within this block',
                 ['Overall block']+candidates[:28],key=f"focus_{subject}_{area}_{selection}")
            if focus!='Overall block':
                topic['title']=focus
                topic['source']='Topic within '+topics[selection]['title']+'. '+topic['source']
    if topic['kind']=='school':st.caption('DBSJP teaching map · Year '+str(topic['year'])+' · source: '+topic['file'])
    else:st.caption('Course index topic · map to the exact micro-specification before authoritative exam-board claims')
    if 'BTEC' in course.get('kind','') or 'BTEC' in subject:tier='Not tiered'
    elif subject in ('Mathematics','Combined Science','Separate Sciences'):tier=st.radio('Tier',['Higher','Foundation'],horizontal=True)
    else:tier='As taught'
    if not course['spec_verified']:
        st.caption('⚠️ Course/code mapping is recorded, but full specification-point checking remains to be completed. Marks are practice estimates.')
    if st.session_state.question_key and st.session_state.question_key[:4]!=(subject,area,topic['title'],tier):reset_q()
    show_subject_library(course,topic,area)
    st.markdown('### Choose how to study')
    option=st.radio('Learning pathway',['Learn the topic','Exam practice'],
        key='revision_route',horizontal=True,
        help='Learn explains and checks understanding; Exam practice generates an original marked task with optional improvement.')
    if option=='Learn the topic':
        st.caption('Understand → worked example → retrieval check → exam practice')
        revise(course,area,topic,tier)
    else:
        st.caption('Attempt → feedback → second attempt → next recommended step')
        testing(course,area,topic,tier)

if __name__=='__main__':main()
