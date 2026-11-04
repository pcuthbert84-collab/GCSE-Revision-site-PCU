"""DBSJP Revision Hub - Mathematics 4MA1 Higher Tier, initial prototype.
Run: streamlit run app.py
"""
import json
import secrets
from datetime import datetime
import streamlit as st
from courses.maths_4ma1 import COURSE, TOPICS, SKILLS, get_skill
from engine.questions import make_question
from engine.marking import mark
from engine.progress import make_attempt, summaries, next_difficulty

st.set_page_config(page_title='DBSJP | Revision Hub',page_icon='📘',layout='wide')
st.markdown('''<style>
.block-container {max-width:1100px; padding-top:2rem}
.muted {color:#64748b;font-size:.9rem}
.brand {font-size:.9rem;letter-spacing:.09em;font-weight:700;color:#64748b}
</style>''',unsafe_allow_html=True)

STATE={'attempts':[], 'question':None,'stage':'new','first':None,'second':None,'difficulty':'Standard', 'recent':[], 'student_work':'', 'first_response':'', 'second_response':'','route':'Revise'}
for k,v in STATE.items():
    if k not in st.session_state: st.session_state[k]=v.copy() if isinstance(v,list) else v

def clear_question():
    for k,v in [('question',None),('stage','new'),('first',None),('second',None),('student_work',''),('first_response',''),('second_response','')]:st.session_state[k]=v

def new_question(skill_id, level):
    for _ in range(20):
        q=make_question(skill_id,level,seed=secrets.randbits(48))
        if q['signature'] not in st.session_state['recent'][-12:]: break
    st.session_state.recent.append(q['signature'])
    st.session_state.question=q
    st.session_state.stage='answer'
    st.session_state.first_response=''
    st.session_state.second_response=''
    st.session_state.student_work=''
    st.session_state.first=None
    st.session_state.second=None

def finish(revealed=False):
    q=st.session_state.question
    if not q:return
    a=make_attempt(q,st.session_state.first,st.session_state.second,revealed)
    st.session_state.attempts.append(a)
    st.session_state.difficulty=next_difficulty(q['difficulty'],a['first_correct'],a['second_correct'],a['revealed'])
    st.session_state.stage='finished'

def revision_content(skill):
    sid=skill['id']
    if sid=='quadratic_factorise':
        st.markdown('### Factorising a quadratic')
        st.write('For a quadratic of the form **x² + bx + c = 0**, look for two numbers that add to **b** and multiply to **c**.')
        st.latex(r'x^2+5x+6=0\quad\Rightarrow\quad(x+2)(x+3)=0')
        st.latex(r'x=-2\quad\text{or}\quad x=-3')
        st.info('Common mistake: giving only one root. A quadratic equation can have two roots.')
    elif sid=='quadratic_formula':
        st.markdown('### The quadratic formula')
        st.latex(r'ax^2+bx+c=0\quad\Rightarrow\quad x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}')
        st.write('Identify **a**, **b** and **c**, substitute carefully, and evaluate both the + and − possibilities.')
        st.info('Common mistake: forgetting brackets when b is negative, or forgetting the ±.')
    elif sid=='percentage_change':
        st.markdown('### Percentage increase and decrease')
        st.write('Calculate the change, then add or subtract it from the original amount. Alternatively use a multiplier.')
        st.latex(r'\text{New value}=\text{Original value}\times(1\pm\text{percentage}/100)')
        st.info('Common mistake: treating a 20% decrease as multiply by 0.20, not 0.80.')
    elif sid=='ratio_share':
        st.markdown('### Sharing in a ratio')
        st.write('Add the parts, divide the total by the number of parts, and multiply by each share.')
        st.latex(r'\text{Share } 150 \text{ in the ratio } 2:3 \Rightarrow 60:90')
        st.info('Common mistake: dividing by one part of the ratio instead of the total number of parts.')
    st.markdown('#### Approved starting points')
    st.link_button('Official Pearson qualification and specification',COURSE['specification_url'])
    st.link_button('BBC Bitesize GCSE Maths', 'https://www.bbc.co.uk/bitesize/subjects/z38pycw')
    st.caption('General resource links only in this prototype. Exact subtopic resources must be manually approved before wider release.')

def test_view(skill):
    st.subheader('Test myself')
    st.write('One original question at a time. Try independently, then improve your answer after feedback.')
    st.caption('Prototype marking checks the final answer exactly. It does not yet award exam-style method marks or grade written working.')
    if st.session_state.question is not None and st.session_state.question['skill_id']!=skill['id']:
        clear_question()
    if st.session_state.question is None:
        c1,c2=st.columns([1,2]);
        with c1:st.selectbox('Starting difficulty',['Foundation','Standard','Challenge'],key='difficulty')
        with c2:st.write('');st.write('');st.button('Generate a question',type='primary',on_click=new_question,args=(skill['id'],st.session_state.difficulty))
        return
    q=st.session_state.question
    st.markdown(f"**{skill['topic']} · {skill['name']}**")
    st.caption(f"{q['difficulty']} · {q['marks']} marks · Original exam-style question · {skill['spec_ref']}")
    st.markdown(q['prompt'])
    if st.session_state.stage=='answer':
        st.text_area('Show your working (optional, not auto-marked yet)',key='student_work',height=120)
        st.text_input('Final answer',key='first_response',placeholder='For two values enter e.g. -2, 3')
        if st.button('Check my first answer',type='primary',disabled=not st.session_state.first_response.strip()):
            st.session_state.first=mark(q,st.session_state.first_response,st.session_state.student_work)
            st.session_state.stage='feedback';st.rerun()
    elif st.session_state.stage=='feedback':
        first=st.session_state.first
        st.success(first['feedback']) if first['correct'] else st.warning(first['feedback'])
        st.caption(first['method_note'])
        if first['correct']:
            if st.button('See solution and finish',type='primary'):
                finish();st.rerun()
        else:
            with st.expander('A hint (without revealing the answer)'):
                st.write(q['hint'])
            st.text_area('Your improved working (optional)',key='student_work',height=100)
            st.text_input('Second attempt: final answer',key='second_response')
            left,right=st.columns(2)
            with left:
                if st.button('Check improved answer',type='primary',disabled=not st.session_state.second_response.strip()):
                    st.session_state.second=mark(q,st.session_state.second_response,st.session_state.student_work)
                    finish();st.rerun()
            with right:
                if st.button('Reveal solution and skip'):
                    finish(revealed=True);st.rerun()
    else:
        if st.session_state.second:
            (st.success if st.session_state.second['correct'] else st.warning)(st.session_state.second['feedback'])
        elif st.session_state.first and st.session_state.first['correct']:
            st.success('Correct independently.')
        else:
            st.info('Solution revealed. This does not count as independent mastery.')
        st.markdown('#### Worked solution')
        st.markdown(q['working'])
        st.caption('Marking guide: '+ '; '.join(q['rubric']))
        st.write('**Suggested next difficulty:**',st.session_state.difficulty)
        if st.button('Next adaptive question',type='primary'):
            new_question(skill['id'],st.session_state.difficulty);st.rerun()

def progress_view():
    st.subheader('My progress')
    st.caption('Progress is saved only in this browser session in V1. Use the JSON export to keep a copy before closing or redeploying.')
    summary=summaries(st.session_state.attempts)
    if not summary:st.info('No practice completed yet. Choose a supported skill and answer a question.');return
    cols=st.columns(3)
    cols[0].metric('Questions completed',len(st.session_state.attempts))
    cols[1].metric('Skills practised',len(summary))
    cols[2].metric('Independent accuracy',f"{100*sum(a['first_correct'] for a in st.session_state.attempts)/len(st.session_state.attempts):.0f}%")
    for topic, skills in SKILLS.items():
        attempted=[s for s in skills if s['id'] in summary]
        if not attempted:continue
        with st.expander(topic,expanded=True):
            for skill in attempted:
                s=summary[skill['id']]
                st.markdown(f"**{skill['name']}** — {s['status']}")
                st.progress(s['first_accuracy'],text=f"First-attempt accuracy: {100*s['first_accuracy']:.0f}% | Attempts: {s['attempts']} | Improved: {s['improved']} | Skipped: {s['skipped']}")
    payload={'course':COURSE['code'],'exported_at':datetime.now().isoformat(timespec='seconds'),'attempts':st.session_state.attempts}
    st.download_button('Download progress as JSON',json.dumps(payload,indent=2),file_name='dbsjp_maths_progress.json',mime='application/json')
    uploaded=st.file_uploader('Restore a previously exported progress file',type=['json'])
    if uploaded and st.button('Restore progress'):
        try:
            data=json.load(uploaded)
            if data.get('course')!=COURSE['code'] or not isinstance(data.get('attempts'),list):raise ValueError('Invalid progress format')
            cleaned=[]
            for a in data['attempts'][:10000]:
                if isinstance(a,dict) and get_skill(a.get('skill_id','')) and isinstance(a.get('first_correct'),bool) and isinstance(a.get('timestamp'),str):
                    cleaned.append({k:a.get(k) for k in ('timestamp','skill_id','difficulty','max_mark','first_correct','second_correct','revealed','signature')})
            st.session_state.attempts=cleaned
            st.success(f'Restored {len(cleaned)} attempts.');st.rerun()
        except (ValueError,TypeError,KeyError,UnicodeDecodeError,json.JSONDecodeError):st.error('Invalid progress export.')

st.markdown('<div class="brand">DBSJP · GCSE REVISION HUB</div>',unsafe_allow_html=True)
st.title('Mathematics Revision')
st.caption('Pearson Edexcel International GCSE Mathematics A (4MA1) · Higher Tier · First prototype')
with st.sidebar:
    st.header('Navigate')
    page=st.radio('Section',['Learn & test','My progress','Past papers','About this prototype'],label_visibility='collapsed')
    st.divider()
    st.caption('V1 • Free • No student accounts yet • No AI API charges')

if page=='Learn & test':
    area=st.selectbox('Choose an area',list(TOPICS))
    topic=st.selectbox('Choose an official topic',TOPICS[area])
    skills=SKILLS.get(topic,[])
    available=[s for s in skills if s['enabled']]
    if not available:
        st.info('This topic is mapped for navigation. Interactive teaching and assessment will be enabled in a later stage.')
        st.link_button('View official specification',COURSE['specification_url'])
    else:
        options={s['name']:s for s in skills}
        label=st.selectbox('Choose a specific skill',list(options))
        skill=options[label]
        if not skill['enabled']:
            st.info('This subtopic is planned but is not assessed yet.')
        else:
            tab1,tab2=st.tabs(['📚 Revise','📝 Test myself'])
            with tab1:revision_content(skill)
            with tab2:test_view(skill)
elif page=='My progress':progress_view()
elif page=='Past papers':
    st.subheader('Official past-paper practice')
    st.write('Use Pearson’s official qualification page to find past papers and mark schemes for **4MA1 Higher Tier**, including **1H** and **2H** where publicly available.')
    st.link_button('Open Pearson Mathematics A',COURSE['specification_url'])
    st.warning('This prototype does not copy, scrape, or automatically mark genuine past-paper questions. Check copyright and licensing before adding such features.')
elif page=='About this prototype':
    st.subheader('What works in V1')
    st.write('Specification-led navigation; four original question generators; exact-answer checking with SymPy; optional improvement attempt; adaptive difficulty; session-only progress; JSON export/import; official past-paper links.')
    st.subheader('What is deliberately not included yet')
    st.write('No automatic AI questions or AI feedback, persistent database, student or parent login, invitation system, method-mark grading, or approved topic-specific resource library. These require subsequent implementation and testing.')
    st.info('Do not enter real student personal data. Nothing is currently sent to a model or external database.')
