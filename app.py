"""DBSJP Revision Hub: all school-booklet subject pathways, no paid services required.
Run from repository root: streamlit run app.py
"""
import json
import secrets
from datetime import datetime, timezone
import streamlit as st
from courses.catalog import CATALOG, all_topics
from courses.maths_4ma1 import SKILLS, get_skill
from engine.questions import make_question
from engine.marking import mark
from engine.ai import get_key,generate,feedback,AIUnavailable
from engine.offline import question as offline_question

st.set_page_config(page_title='DBSJP | Revision Hub',page_icon='📚',layout='wide')
st.markdown('''<style>.block-container{max-width:1120px;padding-top:1.7rem}
.small-muted{color:#667085;font-size:.86rem}.stApp h1{letter-spacing:-.025em}</style>''',unsafe_allow_html=True)

DEFAULTS={'records':[],'active_question':None,'stage':'new','first_answer':'','second_answer':'',
          'first_result':None,'second_result':None,'last_context':None,'mode':'Revise','working':'',
          'subject':'Mathematics','active_difficulty':'Standard'}
for key,value in DEFAULTS.items():
    if key not in st.session_state:st.session_state[key]=value.copy() if isinstance(value,list) else value

def reset_question():
    for k in ['active_question','first_result','second_result','last_context']:
        st.session_state[k]=None
    for k in ['first_answer','second_answer','working']:
        st.session_state[k]=''
    st.session_state.stage='new'

def add_record(context,first,second,skipped):
    rec={'date':datetime.now(timezone.utc).isoformat(timespec='seconds'), 'subject':context['subject'],
         'area':context['area'],'topic':context['topic'],'skill':context.get('skill'),
         'difficulty':context['difficulty'],'practice_type':context['kind'],
         'first_result':first,'second_result':second,'skipped':skipped}
    st.session_state.records.append(rec)
    st.session_state.stage='complete'

def note_band(items):
    if not items:return 'Not yet assessed'
    reliable=[r for r in items if r['practice_type']=='maths-verified' and r.get('first_result') is not None]
    if len(reliable)>=3:
        rate=sum(float(r['first_result']) for r in reliable)/len(reliable)
        if rate>=.8:
            different_days=len({r.get('date','')[:10] for r in reliable})>=2
            return 'Secure (provisional)' if len(reliable)>=5 and different_days else 'Working towards secure'
        if rate>=.5:return 'Developing'
        return 'Priority'
    return 'Practice recorded · limited evidence'

def intro():
    st.title('DBSJP Revision Hub')
    st.caption('School course catalogue · Revise · Test · Improve · Track progress')
    c1,c2,c3=st.columns(3)
    c1.metric('DBSJP pathways',len(CATALOG))
    c2.metric('Booklet-level topics',all_topics())
    c3.metric('Completed practice',len(st.session_state.records))
    if not get_key():st.info('Free offline mode is active. Add an optional Gemini free-tier API key for AI-created questions and personalised feedback. No account or payment needed to use the offline activities.')
    st.caption('This is a single-browser prototype. It does not yet have student accounts or private, persistent progress storage.')

def practice_page():
    st.subheader('Choose a subject')
    chosen=st.selectbox('Subject',list(CATALOG),key='subject')
    c=CATALOG[chosen]
    label=f"{c['kind']}"+(f" · {c['board']}" if c.get('board') else '')+(f" · {c['code']}" if c.get('code') else '')
    st.caption(label)
    if not c['spec_verified']:
        st.warning('Course themes below come from the DBSJP options booklet or a provisional teaching overview. The exact awarding-body specification has NOT yet been verified for this pathway. Practice is for learning, not authenticated exam-board past-paper practice.')
    else:
        st.success('Course identification confirmed. The detailed skill map for this qualification should still be checked before claiming full specification coverage.')
    if c.get('note'):st.caption('Booklet note: '+c['note'])
    area=st.selectbox('Choose an area',list(c['themes']),key=f'area_{chosen}')
    topics_here=list(c['themes'][area])
    if chosen=='Mathematics':
        topics_here.sort(key=lambda t:(t not in ['Percentages','Ratio and proportion','Quadratic equations'],c['themes'][area].index(t)))
    topic=st.selectbox('Choose a topic',topics_here,key=f'topic_{chosen}_{area}')
    chosen_skill=None
    if chosen=='Mathematics':
        # The original interactive maths skills have precise methods and exact marking.
        found=[s for group in SKILLS.values() for s in group if s['enabled'] and s['topic'].split(' ',1)[-1].lower()==topic.lower()]
        if found:
            chosen_skill=st.selectbox('Verified interactive skill',found,format_func=lambda s:s['name'])
            st.caption('This skill uses the original deterministic SymPy-checked mathematics engine.')
    mode=st.radio('What would you like to do?', ['Revise','Test myself'],horizontal=True,key='practice_mode')
    context={'subject':chosen,'area':area,'topic':topic,'skill':chosen_skill['id'] if chosen_skill else None,'difficulty':st.session_state.active_difficulty,'kind':''}
    if mode=='Revise':
        st.markdown('### Revision: '+topic)
        st.write('**Learning target:** Explain the key knowledge in this topic, apply it to an example and identify a common mistake.')
        if chosen_skill:legacy_revision(chosen_skill['id'])
        else:
            st.markdown('**Use this structured revision routine:**')
            st.markdown('1. Write down the key terms or techniques from your lesson notes.\n2. Explain the idea in your own words, then give a specific example.\n3. Check against your course textbook or teacher materials.\n4. Record one common error and how to avoid it.\n5. Test yourself using the button below.')
            if chosen=='Combined Science':st.caption('For science, pay particular attention to key vocabulary, required practicals, calculations and explanations.')
            elif 'BTEC' in chosen:st.caption('For BTEC, use practical assignments, evidence and applied scenarios. These are not automatically treated as written GCSE exam units.')
            elif chosen in ('English Language','English Literature','History','Geography'):st.caption('Use evidence, explanation and subject-specific command words. Extended answers require carefully moderated marking.')
        st.markdown('#### Sources and resources')
        if chosen=='Mathematics':st.link_button('Pearson Maths A qualification','https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses/international-gcse-mathematics-a-2016.html')
        if chosen=='Combined Science':st.link_button('AQA Trilogy qualification','https://www.aqa.org.uk/subjects/science/gcse/science-8464')
        st.link_button('BBC Bitesize GCSE revision','https://www.bbc.co.uk/bitesize/levels/z98jmp3')
        st.caption('Bitesize is a general starting point, not a verified exact-course link for every topic. Approved topic-specific links are a planned editorial feature.')
        if st.button('Test myself on this topic',type='primary'):
            st.session_state.practice_mode='Test myself';st.rerun()
    if mode=='Test myself':
        st.divider()
        st.markdown('### Test myself: '+topic)
        test_ui(context,c,chosen_skill)

def legacy_revision(sid):
    if sid=='quadratic_factorise':
        st.write('To solve a monic quadratic by factorising, find two numbers that add to the coefficient of x and multiply to the constant.')
        st.latex(r'x^2+5x+6=0\Rightarrow(x+2)(x+3)=0\Rightarrow x=-2\ \text{or}\ x=-3')
        st.info('Remember both solutions.')
    elif sid=='quadratic_formula':
        st.latex(r'ax^2+bx+c=0\quad\Longrightarrow\quad x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}')
        st.info('Identify a, b and c carefully; evaluate both signs.')
    elif sid=='percentage_change':
        st.latex(r'\text{new amount}=\text{old amount}\times(1\pm\text{percent}/100)')
        st.info('For a decrease, use a multiplier less than 1.')
    elif sid=='ratio_share':
        st.write('Add the ratio parts, divide the total by the sum, then multiply by each part.')
        st.latex(r'150\text{ in }2:3\quad\Rightarrow\quad 60:90')

def next_level(level,result,skipped):
    ordered=['Foundation','Standard','Challenge']; idx=ordered.index(level)
    if skipped or result is None or result<.5:return ordered[max(0,idx-1)]
    if result>=.9:return ordered[min(2,idx+1)]
    return level

def make_new(context,c,skill):
    difficulty=st.session_state.active_difficulty
    context['difficulty']=difficulty
    if skill is not None:
        q=make_question(skill['id'],difficulty,seed=secrets.randbits(50))
        kind='maths-verified'
    elif get_key():
        try:
            q=generate(c,context['area'],context['topic'],difficulty=difficulty)
            q['source']='ai';kind='ai'
        except AIUnavailable as e:
            st.warning(str(e));q=offline_question(c,context['area'],context['topic']);kind='offline'
    else:
        q=offline_question(c,context['area'],context['topic']);kind='offline'
    context['kind']=kind
    st.session_state.active_question=q
    st.session_state.last_context=context.copy()
    st.session_state.stage='first'
    st.session_state.first_answer='';st.session_state.second_answer='';st.session_state.working=''
    st.session_state.first_result=None;st.session_state.second_result=None

def score_answer(q,answer,kind):
    if kind=='maths-verified':
        graded=mark(q,answer,st.session_state.working)
        return 1.0 if graded['correct'] else 0.0,graded['feedback']
    if kind=='ai':
        try:
            resp=feedback(q,answer)
            return resp['tentative_mark']/q['marks'],f"What went well: {resp.get('strengths','')}\n\nNext step: {resp.get('improvement','')}\n\nIndicative mark: {resp['tentative_mark']}/{q['marks']} (AI estimate, {resp.get('confidence','unknown')} confidence)."
        except AIUnavailable as e:
            return None,'Automated feedback was unavailable. '+str(e)+' Review your answer against the success criteria and try again.'
    return None,'Use the success criteria below to reflect on your answer. This offline activity cannot give a reliable mark.'

def test_ui(context,c,skill):
    current=st.session_state.last_context
    same=current and all(current.get(k)==context.get(k) for k in ('subject','area','topic','skill'))
    if not same:reset_question()
    q=st.session_state.active_question
    if q is None:
        st.selectbox('Starting difficulty',['Foundation','Standard','Challenge'],key='active_difficulty')
        if skill is None:
            st.caption('With a Gemini key: original AI questions with indicative marking. Without one: free retrieval prompts with self-assessment, not examiner marks.')
        if st.button('Generate practice question',type='primary'):
            make_new(context,c,skill);st.rerun()
        return
    kind=st.session_state.last_context['kind']
    st.caption(('Exact-answer mathematics practice' if kind=='maths-verified' else 'AI original practice · indicative marking' if kind=='ai' else 'Offline practice · self-assessment')+' · '+st.session_state.last_context['difficulty'])
    st.markdown(q['prompt'])
    if st.session_state.stage=='first':
        if kind=='maths-verified':
            st.text_area('Show your working (not yet automatically awarded method marks)',key='working',height=100)
            st.text_input('Final answer',key='first_answer',placeholder='Example: -2, 3')
        else:st.text_area('Your answer',key='first_answer',height=175)
        if st.button('Check my first answer',type='primary',disabled=not st.session_state.first_answer.strip()):
            val,msg=score_answer(q,st.session_state.first_answer,kind)
            st.session_state.first_result=val;st.session_state.feedback_text=msg;st.session_state.stage='feedback';st.rerun()
    elif st.session_state.stage=='feedback':
        st.info(st.session_state.feedback_text)
        if kind=='offline':
            st.markdown('**Self-check criteria:**')
            for item in q['marking_points']:st.markdown('- '+item)
            st.caption('This is formative practice. No automatic mark or mastery is claimed.')
        with st.expander('Hint'):
            st.write(q.get('hint','Review key terms and explain your reasoning.'))
        if kind=='maths-verified' and st.session_state.first_result==1.0:
            if st.button('View worked solution and finish',type='primary'):
                add_record(st.session_state.last_context,st.session_state.first_result,None,False);st.rerun()
        else:
            st.write('**Try improving your answer, or reveal the solution and move on.**')
            if kind=='maths-verified':
                st.text_input('Improved final answer',key='second_answer')
            else:st.text_area('Improved answer',key='second_answer',height=140)
            c1,c2=st.columns(2)
            with c1:
                if st.button('Submit improved answer',type='primary',disabled=not st.session_state.second_answer.strip()):
                    val,msg=score_answer(q,st.session_state.second_answer,kind)
                    st.session_state.second_result=val;st.session_state.second_feedback=msg
                    add_record(st.session_state.last_context,st.session_state.first_result,val,False);st.rerun()
            with c2:
                if st.button('Reveal / skip'):
                    add_record(st.session_state.last_context,st.session_state.first_result,None,True);st.rerun()
    elif st.session_state.stage=='complete':
        if st.session_state.second_result is not None:
            st.info(st.session_state.get('second_feedback','Second attempt recorded.'))
        st.markdown('#### Review')
        if kind=='maths-verified':st.markdown(q['working'])
        elif kind=='ai':st.write(q['model_answer']);st.markdown('**Marking criteria:**');st.write('; '.join(q['marking_points']))
        else:
            st.write('Compare your response with your teacher notes or textbook. Your own response has been recorded as practice, but not automatically graded.')
            for point in q['marking_points']:st.markdown('- '+point)
        last=st.session_state.records[-1]
        st.session_state.active_difficulty=next_level(last['difficulty'],last['first_result'],last['skipped'])
        st.caption('Next suggested difficulty: '+st.session_state.active_difficulty)
        if st.button('Next question',type='primary'):
            make_new(context,c,skill);st.rerun()

def progress_page():
    st.subheader('My progress')
    st.warning('V2 prototype: progress exists only in this browser session. For multiple students we must add authenticated accounts and private database storage before deployment.')
    rows=st.session_state.records
    if not rows:st.info('No questions attempted yet. Visit Revise & Test to begin.');return
    c1,c2,c3=st.columns(3)
    c1.metric('Activities completed',len(rows));c2.metric('Subjects attempted',len({r['subject'] for r in rows}));c3.metric('Skipped',sum(r['skipped'] for r in rows))
    for subject in sorted({r['subject'] for r in rows}):
        items=[r for r in rows if r['subject']==subject]
        with st.expander(f'{subject} · {note_band(items)}',expanded=True):
            st.write(f'{len(items)} activities recorded')
            for area in sorted({r['area'] for r in items}):
                st.markdown('**'+area+'**')
                for topic in sorted({r['topic'] for r in items if r['area']==area}):
                    subset=[r for r in items if r['area']==area and r['topic']==topic]
                    st.write(f"{topic}: {note_band(subset)} · {len(subset)} attempts · {sum(r['skipped'] for r in subset)} skips")
    data={'version':2,'exported_at':datetime.now(timezone.utc).isoformat(),'records':rows}
    st.download_button('Export progress (JSON)',json.dumps(data,indent=2),file_name='dbsjp_progress.json',mime='application/json')
    upload=st.file_uploader('Restore previous export',type=['json'])
    if upload and st.button('Restore saved progress'):
        try:
            content=json.load(upload)
            records=content.get('records')
            if not isinstance(records,list) or len(records)>20000:raise ValueError()
            cleaned=[]
            for item in records:
                if not isinstance(item,dict) or item.get('subject') not in CATALOG or not isinstance(item.get('topic'),str):raise ValueError()
                cleaned.append({k:item.get(k) for k in ('date','subject','area','topic','skill','difficulty','practice_type','first_result','second_result','skipped')})
            st.session_state.records=cleaned;st.success(f'Restored {len(cleaned)} activities.');st.rerun()
        except Exception:st.error('Invalid or unsupported export file.')

def papers_page():
    st.subheader('Genuine past papers')
    st.write('These are **external official publisher links**, not copies of examination papers or mark schemes.')
    st.link_button('Pearson Edexcel qualifications','https://qualifications.pearson.com/en/qualifications.html')
    st.link_button('AQA qualifications','https://www.aqa.org.uk/subjects')
    st.link_button('OCR qualifications','https://www.ocr.org.uk/qualifications/')
    st.caption('Choose the exact school qualification and paper on the awarding body’s website. Not all course codes have been verified; this prototype does not scrape or automatically mark copyrighted past-paper questions.')

def admin_page():
    st.subheader('Course catalogue & quality checks')
    st.warning('Administrator login and approval workflow are NOT implemented yet. This page is publicly visible in the current prototype; do not upload private student or school data.')
    for name,c in CATALOG.items():
        with st.expander(name):
            st.write(f"Qualification: {c['kind']} | Board: {c.get('board') or 'To verify'} | Code: {c.get('code') or 'To verify'}")
            st.write('Source status: '+('Verified qualification identifier / configured topic structure' if c['spec_verified'] else 'Booklet themes / provisional, official specification mapping required'))
            st.write(f"{sum(len(v) for v in c['themes'].values())} listed themes")
            if c.get('note'):st.caption(c['note'])
    st.markdown('#### Before a school-wide launch')
    st.write('Confirm board, specification number and exam series for every course; obtain appropriate data-protection and safeguarding approval; add secure identity and row-level access controls; validate AI data terms; approve topic-level source links and representative assessment samples.')

def about_page():
    st.subheader('About this build')
    st.write('This expands the original Mathematics prototype into a 28-pathway DBSJP revision catalogue, based on the 2026–27 school options booklet. It is not yet a fully populated or independently validated official-specification library for every course.')
    st.write('Mathematics has four deterministic, automatically marked question skills. Other pathways offer free retrieval-practice prompts and optional original AI questions when a Gemini API key is configured. AI feedback is indicative, not an examination-board mark.')
    st.write('No generated questions are stored in a permanent bank. The active question is held temporarily in Streamlit session state, with compact progress data recorded in that session.')
    st.warning('Do not use with identifiable student data until secure accounts, privacy review and a suitable AI data-processing arrangement are completed.')

with st.sidebar:
    st.markdown('### 📚 DBSJP Revision Hub')
    page=st.radio('Navigate',['Revise & Test','Home','My progress','Past papers','Course catalogue','About'],label_visibility='collapsed')
    st.divider();st.caption('V2 · Multi-subject prototype · Free offline mode')

if page=='Home':
    intro()
    st.markdown('### Start here')
    st.info('Use **Revise & Test** in the left navigation to start. Working Mathematics question types are available; other subjects support free self-check practice, plus optional AI feedback.')
elif page=='Revise & Test':practice_page()
elif page=='My progress':progress_page()
elif page=='Past papers':papers_page()
elif page=='Course catalogue':admin_page()
else:about_page()
