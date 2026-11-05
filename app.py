"""DBSJP Revision Hub V4: content-first subject practice with optional free-tier Gemini.
No student accounts, progress database, permanent question bank or paid endpoints.
"""
import secrets
import json
from urllib.parse import quote
import streamlit as st
from courses.v4_catalog import COURSES, topic_groups
from courses.revision_content import get_content
from courses.maths_4ma1 import SKILLS
from engine.questions import make_question
from engine.marking import mark
from engine.ai import get_key, get_model, get_fallback_model, connection_test, list_available_models, AIUnavailable
from engine.v4_ai import create_study,create_question,evaluate

st.set_page_config(page_title='DBSJP Revision Hub | V4.2',page_icon='📚',layout='wide')
st.markdown('''<style>
.block-container{max-width:1090px;padding-top:1.8rem;padding-bottom:3rem}
[data-testid="stSidebar"]{min-width:260px}
h1,h2,h3{letter-spacing:-.02em}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px}
</style>''',unsafe_allow_html=True)

# Limits are session-level safeguards only. Provider-side free-tier quota / no paid billing
# must be configured independently; shared persistent quota enforcement is out of scope.
MAX_AI_CALLS_PER_SESSION=65
for name,default in {'ai_calls':0,'notes_cache':{},'active_question':None,'attempt_stage':'new',
                     'first_text':'','retry_text':'','first_result':None,'second_result':None,
                     'attempt_summary':[],'reported_issues':[],'question_key':None,'level':'Standard','start_id':0}.items():
    if name not in st.session_state:st.session_state[name]=default

def can_ai():return bool(get_key()) and st.session_state.ai_calls<MAX_AI_CALLS_PER_SESSION

def with_ai(func,*args,**kwargs):
    if not can_ai():raise AIUnavailable('Gemini key missing or this browser session has reached its AI-call safety cap.')
    st.session_state.ai_calls+=1
    return func(*args,**kwargs)

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

def render_notes(note):
    st.markdown('#### Learning outcomes')
    for p in note['outcomes']:st.markdown('- '+str(p))
    st.markdown('#### Understand the topic')
    st.write(note['explanation'])
    st.markdown('#### Essential knowledge')
    for p in note['key_points']:st.markdown('- '+str(p))
    st.markdown('#### Worked example')
    st.info(note['worked_example'])
    st.markdown('#### Common mistakes')
    for p in note['pitfalls']:st.markdown('- '+str(p))
    with st.expander('Quick retrieval checks (with answers)'):
        for i,item in enumerate(note['quick_check'],1):
            if not isinstance(item,dict):continue
            st.markdown(f"**{i}. {item.get('question','')}**")
            st.write(item.get('answer',''))
    if note.get('uncertainty'):st.warning('Content to check: '+note['uncertainty'])
    st.caption('AI-created revision explanation; not approved or written by the examination board. Please report any inaccuracies.')

def revise(course,area,topic,tier):
    st.subheader('Revise · '+topic['title'])
    cached_key=(course['name'],area,topic['title'],tier)
    old=local_notes_for(course['name'],topic['title'])
    if cached_key in st.session_state.notes_cache:
        render_notes(st.session_state.notes_cache[cached_key])
    elif old:
        st.markdown('#### What you need to know');st.write(old['goal'])
        st.markdown('#### Essential knowledge')
        for p in old['points']:st.markdown('- '+p)
        st.info('**Worked explanation:** '+old['example'])
        st.warning('**Common mistake:** '+old['mistake'])
        if can_ai() and st.button('Create a more detailed revision guide',key='upgrade_notes'):
            try:
                with st.spinner('Preparing a topic-specific explanation…'):
                    st.session_state.notes_cache[cached_key]=with_ai(create_study,course,topic,area,tier)
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
                        st.session_state.notes_cache[cached_key]=with_ai(create_study,course,topic,area,tier)
                    st.rerun()
                except AIUnavailable as ex:st.warning(str(ex))
        else:
            st.warning('A full explanation for this topic is not prewritten. Add the free Gemini API key in Streamlit Secrets to generate it, or use the original school course outline above.')
    st.divider()
    st.markdown('#### Free resources')
    if course.get('board','').startswith('AQA'):
        st.link_button('Browse AQA subject materials','https://www.aqa.org.uk/subjects')
    elif 'Pearson' in str(course.get('board','')):
        st.link_button('Browse Pearson qualifications','https://qualifications.pearson.com/en/qualifications.html')
    st.link_button('BBC Bitesize GCSE','https://www.bbc.co.uk/bitesize/levels/z98jmp3')
    st.link_button('Search free topic explanations', 'https://www.google.com/search?q='+quote(course['name']+' '+topic['title']+' GCSE revision'))
    st.caption('General resource entry points until each external resource is manually reviewed for syllabus accuracy.')

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

def new_question(course,area,topic,tier,difficulty):
    local=make_local_question(course,topic,difficulty)
    if can_ai():
        try:
            with st.spinner('Creating and checking a new question…'):
                q=with_ai(create_question,course,topic,area,tier,difficulty)
            return {'kind':'ai','data':q,'prompt':q['prompt'],'max_marks':q['max_marks']}
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
                res=with_ai(evaluate,q['data'],answer,second=second)
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
    if res['strength']:st.markdown('**What went well:** '+res['strength'])
    if res['next']:st.markdown('**Next step:** '+res['next'])
    if first:st.caption('Feedback should help you improve without revealing the full solution. Marks on extended responses are provisional.')

def solution(q):
    st.markdown('#### Model answer and criteria')
    if q['kind']=='exact':
        st.markdown(q['data']['working'])
        for item in q['data'].get('rubric',[]):st.markdown('- '+item)
        st.caption('Exemplar method only. Other correct mathematical methods must also earn credit.')
    elif q['kind']=='guided':
        st.write(q['data']['model'])
        for item in q['data'].get('points',[]):st.markdown('- '+item)
    else:
        st.write(q['data']['model_answer'])
        for item in q['data']['marking_points']:
            st.markdown(f"- **{item['credit']} mark(s):** {item['criterion']}")
        if q['data'].get('uncertainty'):st.warning('Check: '+q['data']['uncertainty'])
    st.caption('This is an original learning example, not an official past-paper mark scheme.')

def testing(course,area,topic,tier):
    st.subheader('Test yourself · '+topic['title'])
    context=(course['name'],area,topic['title'],tier)
    if st.session_state.question_key and st.session_state.question_key[:4]!=context:reset_q()
    if st.session_state.active_question is None:
        difficulty=st.select_slider('Difficulty',['Foundation','Standard','Challenge'],value=st.session_state.level,key='question_difficulty')
        st.write('One question at a time, one answer box for all working, personalised feedback and an optional second attempt.')
        if not can_ai():st.caption('AI is currently unavailable or has reached this session’s cap. Prewritten questions will be offered where available.')
        if st.button('Generate a question',type='primary'):
            q=new_question(course,area,topic,tier,difficulty)
            if q:
                st.session_state.active_question=q;st.session_state.question_key=context+(difficulty,)
                st.session_state.attempt_stage='first';st.rerun()
            else:st.warning('No reviewed offline question exists for this topic. Set a Gemini API key to enable original question generation.')
        return
    q=st.session_state.active_question
    st.caption(f"Original practice · {st.session_state.question_key[-1]} · {q['max_marks']} marks · {('AI-generated, provisional' if q['kind']=='ai' else 'Locally generated')}")
    st.markdown(q['prompt'])
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
            st.write(q['data'].get('hint','Review the question carefully.'))
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

def main():
    with st.sidebar:
        st.title('📚 DBSJP Revision Hub')
        page=st.radio('Navigation',['Revise & Test','AI connection test','Official past papers','Testing issues','How this prototype works'])
        st.divider()
        st.caption('V4.4 • Content-first • Level 2 only')
        st.caption('No accounts or stored progress')
        st.caption(('Gemini key configured (not yet verified)' if get_key() else 'Gemini not configured')+f' · {st.session_state.ai_calls}/{MAX_AI_CALLS_PER_SESSION} session calls')
        if get_key():st.caption('Each new AI guide, question or marking attempt uses the shared API project’s free allowance.')
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
        st.write('Review the issues flagged during this browser session. These are not uploaded anywhere or saved to a database.')
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
        st.write('This release covers DBSJP Level 2 subjects and includes teaching maps from school documents, original AI question generation, second attempts and indicative feedback. No accounts or data are saved to a progress database.')
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
    option=st.radio('What would you like to do?',['📖 Revise','✏️ Test myself'],horizontal=True)
    if option.startswith('📖'):revise(course,area,topic,tier)
    else:testing(course,area,topic,tier)

if __name__=='__main__':main()
