"""DBSJP Revision Hub V3: content-first pilot, no accounts, no progress data."""
import secrets
import streamlit as st
from courses.catalog import CATALOG
from courses.maths_4ma1 import SKILLS
from courses.revision_content import get_content, coverage_count
from engine.questions import make_question
from engine.marking import mark
from engine.ai import get_key, generate, feedback, AIUnavailable

st.set_page_config(page_title='DBSJP Revision Hub',page_icon='📚',layout='wide')
st.markdown('''<style>.block-container{max-width:1000px;padding-top:1.5rem}
[data-testid="stSidebar"]{min-width:230px}</style>''',unsafe_allow_html=True)

MATH_SKILLS={
    'quadratic_factorise':('Quadratic equations','Factorising quadratics'),
    'quadratic_formula':('Quadratic equations','Quadratic formula'),
    'percentage_change':('Percentages','Percentage change'),
    'ratio_share':('Ratio and proportion','Sharing in a ratio'),
}

if 'qa' not in st.session_state: st.session_state.qa=None
if 'qa_context' not in st.session_state: st.session_state.qa_context=None
if 'step' not in st.session_state: st.session_state.step='first'
if 'first_answer' not in st.session_state: st.session_state.first_answer=''
if 'second_answer' not in st.session_state: st.session_state.second_answer=''
if 'working' not in st.session_state: st.session_state.working=''
if 'first_feedback' not in st.session_state: st.session_state.first_feedback=''
if 'first_correct' not in st.session_state: st.session_state.first_correct=None
if 'second_feedback' not in st.session_state: st.session_state.second_feedback=''
if 'question_counter' not in st.session_state: st.session_state.question_counter=0
if 'mode' not in st.session_state: st.session_state.mode='Revise'

def clear_question():
    st.session_state.qa=None
    st.session_state.qa_context=None
    st.session_state.step='first'
    st.session_state.first_answer=''
    st.session_state.second_answer=''
    st.session_state.working=''
    st.session_state.first_feedback=''
    st.session_state.first_correct=None
    st.session_state.second_feedback=''

def maths_for(topic):
    return [dict(id=sid,name=label,original=next((s for row in SKILLS.values() for s in row if s['id']==sid),None))
            for sid,(t,label) in MATH_SKILLS.items() if t==topic]

def display_study(content, subject, topic, math_skill):
    st.subheader('Revise: '+topic)
    if math_skill:
        st.caption('Original worked teaching example · Pearson Edexcel Mathematics A (4MA1), Higher Tier')
        sid=math_skill['id']
        descriptions={
            'quadratic_factorise':('To factorise a monic quadratic, find two numbers whose sum is the coefficient of x and whose product is the constant term.',r'x^2+5x+6=0\Rightarrow(x+2)(x+3)=0\Rightarrow x=-2\text{ or }x=-3','Always give both roots.'),
            'quadratic_formula':('For a quadratic in the form ax² + bx + c = 0, identify a, b and c, substitute carefully and evaluate both signs.',r'x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}','Keep the negative signs and brackets correct.'),
            'percentage_change':('Convert a percentage increase or decrease to a multiplier, then multiply by the original value.',r'\text{New value}=\text{Original}\times(1\pm\frac{p}{100})','An increase uses +; a decrease uses −.'),
            'ratio_share':('Add the ratio parts to find the number of equal units. Divide the total by that sum and multiply by each part.',r'150\text{ shared in }2:3\;\Rightarrow\;\frac{150}{5}\times 2=60,\;\frac{150}{5}\times3=90','Check the parts add back to the total.')}
        intro,example,mistake=descriptions[sid]
        st.write(intro);st.latex(example);st.info('Watch out: '+mistake)
    elif content:
        st.markdown('**What you should be able to do**')
        st.write(content['goal'])
        st.markdown('**Essential knowledge and techniques**')
        for point in content['points']: st.markdown('- '+point)
        st.markdown('**Worked example / model explanation**')
        st.info(content['example'])
        st.markdown('**Common mistake**')
        st.warning(content['mistake'])
    else:
        st.info('Detailed revision notes for this topic have not been reviewed yet. We are deliberately not replacing them with generic study instructions or pretending unverified content is exam-board approved.')
        if get_key():
            st.caption('You can still try an original AI-generated practice question below; feedback is provisional and should be checked.')
    st.markdown('#### Further resources')
    if subject=='Mathematics':
        st.link_button('Pearson Edexcel Mathematics A 4MA1','https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses/international-gcse-mathematics-a-2016.html')
    elif subject=='Combined Science':
        st.link_button('AQA Combined Science: Trilogy 8464','https://www.aqa.org.uk/subjects/science/gcse/science-8464')
    st.link_button('BBC Bitesize GCSE resources (general)','https://www.bbc.co.uk/bitesize/levels/z98jmp3')
    st.caption('Resources are entry points, not yet a fully checked set of links for each DBSJP specification point.')
    st.button('Test myself on this topic',type='primary',on_click=lambda:setattr(st.session_state,'mode','Test myself'))

def generate_question(course,subject,area,topic,skill,content,difficulty):
    if skill:
        q=make_question(skill['id'],difficulty,seed=secrets.randbits(50))
        return {'kind':'maths','question':q,'prompt':q['prompt']}
    if get_key():
        try:
            q=generate(course,area,topic,difficulty=difficulty)
            return {'kind':'ai','question':q,'prompt':q['prompt']}
        except AIUnavailable as exc: st.warning(str(exc)+' Using reviewed offline material if available.')
    if not content: return None
    examples=content['questions']
    q=examples[st.session_state.question_counter%len(examples)]
    return {'kind':'curated','question':q,'prompt':q['prompt']}

def assess(q,answer,working=''):
    kind=q['kind']; item=q['question']
    if kind=='maths':
        result=mark(item,answer,working)
        return result['feedback'],result['correct']
    if kind=='ai':
        try:
            res=feedback(item,answer)
            return f"**What went well:** {res.get('strengths','')}\n\n**Next step:** {res['improvement']}\n\n*Indicative AI mark: {res['tentative_mark']}/{item['marks']}.*",None
        except AIUnavailable: return 'AI marking is temporarily unavailable. You can still compare your response with the model at the end.',None
    return ('Use the improvement prompts below to strengthen your answer. The offline version deliberately does not claim to assess extended responses automatically.',None)

def test_screen(course,subject,area,topic,math_skill,content):
    st.subheader('Test myself: '+topic)
    ctx=(subject,area,topic,math_skill['id'] if math_skill else None)
    if st.session_state.qa_context and st.session_state.qa_context[:4]!=ctx:clear_question()
    if st.session_state.qa is None:
        if not math_skill and not content and not get_key():
            st.warning('Interactive testing for this topic is not yet available in free offline mode. Choose a prepared topic or configure the optional free AI provider.')
            return
        difficulty=st.selectbox('Question difficulty',['Foundation','Standard','Challenge'],index=1,key='test_difficulty')
        if get_key():st.caption('Gemini enabled: original questions and provisional AI marking. Never submit identifying student information.')
        elif math_skill:st.caption('Original parameterised questions with SymPy final-answer checks. Working is not yet awarded method marks.')
        else:st.caption('Original reviewed practice question with self-assessment; no automated essay marking or stored results.')
        if st.button('Start question',type='primary'):
            new=generate_question(course,subject,area,topic,math_skill,content,difficulty)
            if new:
                st.session_state.qa=new
                st.session_state.qa_context=ctx+(difficulty,)
                st.session_state.step='first'
                st.rerun()
        return
    q=st.session_state.qa
    kind=q['kind']
    st.caption(f"{st.session_state.qa_context[-1]} · {'Exact answer check' if kind=='maths' else 'AI feedback (indicative)' if kind=='ai' else 'Self-check practice'}")
    st.markdown(q['prompt'])
    if st.session_state.step=='first':
        if kind=='maths':
            st.text_area('Show your working',key='working',height=110)
            st.text_input('Final answer',key='first_answer',placeholder='e.g. -2, 3')
        else:st.text_area('Type your answer',key='first_answer',height=160)
        if st.button('Check my answer',type='primary',disabled=not (st.session_state.first_answer.strip() or (kind=='maths' and st.session_state.working.strip()))):
            st.session_state.first_feedback,st.session_state.first_correct=assess(q,st.session_state.first_answer,st.session_state.working)
            st.session_state.step='feedback';st.rerun()
    elif st.session_state.step=='feedback':
        if kind=='maths' and st.session_state.first_correct is True:
            st.success(st.session_state.first_feedback)
            st.caption('Full prototype answer-check credit. Detailed method marks are not assessed yet.')
            if st.button('See the worked example (one possible method)'):
                st.session_state.step='finished';st.rerun()
            if st.button('Try another question',type='primary'):
                st.session_state.question_counter+=1;clear_question();st.rerun()
            return
        elif kind=='maths' and st.session_state.first_correct is None:
            st.warning(st.session_state.first_feedback)
            st.caption('Not marked incorrect. You may clarify your answer or reveal the solution.')
        else:
            st.info(st.session_state.first_feedback)
        if kind=='curated':
            st.markdown('**Check your answer against these success criteria:**')
            for point in q['question']['points']:st.markdown('- '+point)
        else:
            with st.expander('Need a hint?'):
                st.write(q['question'].get('hint','Consider the steps and the question carefully.'))
        st.markdown('**Try again, or reveal the solution.**')
        if kind=='maths':
            st.caption('Different correct methods are welcome. The automatic checker currently scores final-answer accuracy, not method marks.')
        if kind=='maths':st.text_input('Improved final answer',key='second_answer')
        else:st.text_area('Your improved answer',key='second_answer',height=130)
        a,b=st.columns(2)
        with a:
            if st.button('Submit improved answer',type='primary',disabled=not st.session_state.second_answer.strip()):
                st.session_state.second_feedback,_=assess(q,st.session_state.second_answer,st.session_state.working)
                st.session_state.step='finished';st.rerun()
        with b:
            if st.button('Reveal solution / skip'):
                st.session_state.step='finished';st.rerun()
    else:
        if st.session_state.second_feedback:st.info(st.session_state.second_feedback)
        st.markdown('#### Model answer / worked solution')
        if kind=='maths':st.markdown(q['question']['working'])
        elif kind=='ai':
            st.write(q['question']['model_answer'])
            st.markdown('**Marking criteria**')
            for p in q['question']['marking_points']:st.markdown('- '+p)
        else:
            st.write(q['question']['model'])
            st.caption('Use this as an illustrative response, not an official exam-board mark scheme.')
        if st.button('Another question',type='primary'):
            st.session_state.question_counter+=1
            clear_question()
            st.rerun()

def practice_page():
    st.title('Choose a subject')
    subject=st.selectbox('Subject',list(CATALOG),key='chosen_subject')
    c=CATALOG[subject]
    st.caption(f"{c['kind']}"+(f" · {c['board']}" if c.get('board') else '')+(f" · {c['code']}" if c.get('code') else ''))
    if not c['spec_verified']:
        with st.expander('Course verification notice'):
            st.write('The themes for this course come from the DBSJP options booklet or a provisional outline. Its exact awarding-body specification has not yet been verified. These activities are original learning practice, not authenticated examination-board questions.')
    area=st.selectbox('Choose an area',list(c['themes']),key=f'area_{subject}')
    topics=list(c['themes'][area])
    # Put prepared activities first, but retain every booklet-level navigation topic.
    topics.sort(key=lambda t: (not bool(get_content(subject,t) or (subject=='Mathematics' and maths_for(t))),))
    topic=st.selectbox('Choose a topic',topics,key=f'topic_{subject}_{area}')
    content=get_content(subject,topic)
    math_options=maths_for(topic) if subject=='Mathematics' else []
    skill=None
    if math_options:
        skill=st.selectbox('Choose a skill',math_options,format_func=lambda x:x['name'])
    if content or skill:
        st.caption('✓ Detailed revision and interactive practice prepared for this topic')
    else:st.caption('Topic indexed. Detailed revision is being developed.')
    st.radio('What would you like to do?',['Revise','Test myself'],horizontal=True,key='mode')
    current=(subject,area,topic,skill['id'] if skill else None)
    if st.session_state.qa_context and st.session_state.qa_context[:4]!=current:clear_question()
    if st.session_state.mode=='Revise':display_study(content,subject,topic,skill)
    else:test_screen(c,subject,area,topic,skill,content)

with st.sidebar:
    st.markdown('### 📚 DBSJP Revision Hub')
    page=st.radio('Navigate',['Revise & Test','Past papers','About this prototype'],label_visibility='collapsed')
    st.divider()
    st.caption('V3 · Content-first prototype · No accounts or progress storage')
if page=='Revise & Test':practice_page()
elif page=='Past papers':
    st.title('Official past-paper practice')
    st.write('Access published papers on official awarding-body websites. We do not reproduce or automatically mark copyrighted paper questions.')
    st.link_button('Pearson Edexcel qualifications','https://qualifications.pearson.com/en/qualifications.html')
    st.link_button('AQA qualifications','https://www.aqa.org.uk/subjects')
    st.link_button('OCR qualifications','https://www.ocr.org.uk/qualifications/')
    st.warning('Check the exact subject qualification before choosing a paper. Not every DBSJP optional subject has been independently matched to its full code.')
else:
    st.title('About this prototype')
    st.write(f'This version indexes {len(CATALOG)} DBSJP pathways, and has {coverage_count()} editorially written non-Mathematics revision modules plus four interactive Mathematics skills.')
    st.write('The priority is learning content and testing quality. Student accounts, parent access, administration and progress dashboards are deliberately excluded.')
    st.write('For topics without reviewed content, the website shows a clear not-yet-prepared message instead of generic instructions. With a configured Gemini API key, other topics can offer provisional original AI practice.')
    st.warning('Do not enter identifying student data. Free-tier AI services have quotas and separate data-use terms. No exam-board papers are submitted to the AI service.')
