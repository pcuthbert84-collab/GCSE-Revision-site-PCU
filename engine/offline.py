"""Offline non-AI retrieval practice. Not represented as exam-board question marking."""
import random

def question(course,area,topic):
    kind=course['kind'].lower()
    if 'art' in kind or 'design' in kind or 'performing' in kind or 'music' in course['name'].lower() or 'photography' in course['name'].lower():
        templates=[
            f'For **{topic}**, describe a technique you would use in a project. Explain how you would evaluate its success.',
            f'Explain two design or performance decisions involved in **{topic}**, and justify your choices.',
            f'Outline how you would plan, develop and improve work related to **{topic}**.' ]
        checks=['A specific and relevant technique or decision','Reasoning or justification','A realistic way to assess or improve the outcome']
    elif any(k in course['name'] for k in ('French','Spanish','Arabic','English as a Second')):
        templates=[
            f'Using the language you are studying, write 3–4 sentences demonstrating **{topic}**. Include a reason or example.',
            f'Write a short example showing how you would use **{topic}** accurately, then explain one language choice.',
            f'Demonstrate **{topic}** in a short response suitable for your course. Check grammar, vocabulary and meaning.' ]
        checks=['Relevant language produced','Grammar and vocabulary checked','Answer makes sense in the intended context']
    elif 'BTEC' in kind:
        templates=[
            f'Give a realistic workplace or project example involving **{topic}**. Explain the decisions you would make.',
            f'Describe an appropriate procedure or approach for **{topic}**, including how you would check the result.',
            f'Explain how **{topic}** could be applied in a practical assignment, with one specific example.' ]
        checks=['Accurate understanding of the topic','Relevant applied example','Clear justification or evaluation']
    else:
        templates=[
            f'Explain **{topic}** and describe one example showing how the idea can be applied.',
            f'Identify two important principles or facts about **{topic}**. Explain the relationship between them.',
            f'Describe a common misconception about **{topic}** and explain a more accurate understanding.' ]
        checks=['Relevant and accurate subject knowledge','Explanation supported by a specific example','Clear reasoning rather than unsupported assertions']
    return {'prompt':random.choice(templates),'hint':'Recall the key definitions, a specific example and how to explain your reasoning.',
            'marking_points':checks,'model_answer':None,'marks':None,'source':'offline'}
