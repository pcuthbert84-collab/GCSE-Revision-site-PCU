"""Conservative exam-practice modes for the DBSJP Level 2 hub.

Question formats are informed by the Pearson Edexcel International GCSE
qualification, not reproduced from protected exam papers or mark schemes.
Synthetic tasks are explicitly labelled original / indicative. The school
topic map is not evidence of the actual paper option entered by the pupil.
"""
import re

def _combined(area,topic):
    return (str(area)+" "+str(topic.get("title",""))+" "+str(topic.get("source",""))[:800]).lower()

def exam_modes(course, area, topic):
    name=course.get("name","")
    context=_combined(area,topic)
    options=[{
        "id":"short","label":"Short topic practice (2–8 marks)",
        "marks":None,"type":"original topic question",
        "description":"Original question with provisional, topic-specific marking."}]
    if name=="History" and course.get("code")=="4HI1":
        options.append({
            "id":"history_evaluate","label":"Historical judgement (16 marks)",
            "marks":16,"type":"historical evaluation",
            "description":"Original how-far-do-you-agree style question; not an official past-paper item."})
        options.append({
            "id":"history_effects","label":"Explain two effects (8 marks)",
            "marks":8,"type":"causation and consequence",
            "description":"Explain two distinct effects using precise historical knowledge."})
        # Comparison is relevant to the breadth-study change component,
        # not a universal question on every History option.
        if any(word in context for word in ("medicine","surgery","public health","1848","1948")):
            options.append({
                "id":"history_compare","label":"Explain two differences (6 marks)",
                "marks":6,"type":"change over time",
                "description":"Two supported comparisons from relevant periods."})
    if name=="English Literature" and course.get("code")=="4ET1":
        if "unseen" in context and ("poem" in context or "poetry" in context):
            options.append({
                "id":"literature_unseen","label":"Unseen poetry analysis (20 marks)",
                "marks":20,"type":"literary analysis of original poem",
                "description":"Uses a short clearly ORIGINAL poem provided with the question. Indicative rubric."})
        elif any(k in context for k in ("romeo and juliet","mice and men","inspector calls",
                                      "macbeth","modern prose","literary heritage","modern drama")):
            options.append({
                "id":"literature_essay","label":"Literary analysis essay (30 marks)",
                "marks":30,"type":"extended literature argument",
                "description":"Original essay task for a named text. Route/assessment component to be confirmed by teacher."})
    if name=="English Language" and course.get("code")=="4EA1":
        if any(k in context for k in ("transactional","letter","article","speech","writing")):
            options.append({
                "id":"language_writing","label":"Transactional writing (30 practice marks)",
                "marks":30,"type":"audience purpose form writing",
                "description":"Original classroom-practice scale, NOT the official Paper 1 mark allocation."})
    return options

def exam_instruction(mode,course,topic):
    """The model must honour a fixed provisional rubric and declared question type."""
    marks=mode.get("marks")
    if not marks:
        return ""
    name=course.get("name","")
    guidance={
        "history_evaluate":(
            "Ask one historical evaluation ('How far do you agree?') on the exact topic. "
            "Include a proposition anchored to safely established history and require "
            "students to consider at least one competing factor and a justified conclusion. "
            "Create a provisional 16-mark analytic rubric, not a claim of a Pearson mark scheme."),
        "history_effects":(
            "Ask for TWO distinct effects of one accurately identified event/process in the supplied topic. "
            "Require developed explanation of how each effect occurred. Marks: 8."),
        "history_compare":(
            "Ask for TWO clear differences between two specified historical periods or practices "
            "within the selected medicine topic. Marks: 6. No vague cross-topic comparisons."),
        "literature_unseen":(
            "Create a completely ORIGINAL 6–10 line English poem, clearly label it original, "
            "include all lines in prompt, then ask how the writer uses language and structure "
            "to convey a meaning. Do NOT quote a published poem. Evaluate supported "
            "interpretation and technique analysis. Marks: 20 provisional."),
        "literature_essay":(
            "Only ask about the exact named text if supported by the supplied topic. "
            "Ask an original extended analysis of character or theme, allowing varied "
            "interpretations, relevant evidence and writer's choices. Do not invent or "
            "supply quotations, scenes or historical context. Marking is indicative, "
            "not a reproduction of official levels. Marks: 30."),
        "language_writing":(
            "Give a clear original real-world purpose, audience and format (e.g. "
            "a formal letter or speech) for transactional writing. Evaluate clarity, "
            "organisation, persuasive development and accurate language. Do not "
            "claim 30 is the official qualification mark allocation; it is a practice "
            "scale. Marks: 30 provisional."),
    }[mode["id"]]
    return (
        "EXAM PRACTICE MODE: "+name+", "+mode["type"]+". "+guidance+" "
        "The exact maximum mark is "+str(marks)+". Produce original content ONLY. "
        "Rubric: EXACTLY FOUR marking_points, each object {criterion:string,credit:integer}, "
        "positive whole-number credit values summing to "+str(marks)+". "
        "Make criteria sufficiently distinct, measurable and useful for developmental "
        "feedback; the rubric is PROVISIONAL and NOT an official published mark scheme. "
        "For 16 mark answers, give developed evidence-based model analysis; for 20/30 mark "
        "tasks, give a strong but concise modelled outline or original specimen. "
        "Return ONLY JSON: prompt:string, hint:string, model_answer:string, "
        "max_marks:integer, marking_points:array, question_type:string, uncertainty:string. "
        "Do not make the task depend on an unavailable copyrighted source, image or passage. "
        "If accurate stimulus cannot be supplied, return uncertainty explaining the issue "
        "rather than fabricating historical documentation."
    )
