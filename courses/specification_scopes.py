"""Concise, editorial qualification scopes based on published awarding-body pages.

These are NOT full copyrighted specifications or a line-by-line audit.
They provide reliable boundaries, particularly to prevent mixing similar
qualifications or course pathways. School-selected options still need approval.
"""

SCOPES = {
 "Mathematics": (
    "Pearson Edexcel International GCSE Mathematics A, 4MA1, linear. "
    "Practise number, algebra, geometry, statistics, probability and problem "
    "solving appropriate to chosen tier. Exact mathematical equivalence is "
    "more important than copying a model method."),
 "Further Mathematics": (
    "Pearson Edexcel International GCSE Further Pure Mathematics, 4PM1. "
    "Extend mathematical reasoning using algebra, functions, trigonometry, "
    "calculus, geometry and series only where supported by the selected "
    "school topic. Do not substitute standard 4MA1 assessment."),
 "English Language": (
    "Pearson Edexcel International GCSE English Language A, 4EA1. "
    "Distinguish comprehension and analysis of anthology non-fiction, "
    "transactional writing and the optional second-component examination "
    "versus coursework routes. Do not assume students take every route; "
    "the published specification and approved text list take precedence."),
 "English Literature": (
    "Pearson Edexcel International GCSE English Literature, 4ET1. "
    "Analyse language, form, structure, themes and supported interpretations "
    "of selected poetry, prose and drama. Examination and coursework routes "
    "are alternatives, not cumulative requirements; DBSJP selected texts "
    "and route must be confirmed before board-specific question assertions."),
 "English as a Second Language": (
    "Pearson Edexcel International GCSE English as a Second Language "
    "4XES2 is a unitised qualification with reading, writing, listening "
    "and speaking. Teach communication appropriate to CEFR stages, "
    "register, audience and accuracy. Unit codes differ from cash-in code."),
 "History": (
    "Pearson Edexcel International GCSE History 4HI1 has Paper 1 Depth Studies "
    "and Paper 2 investigation and breadth studies. School-selected options "
    "must be confirmed. For UAE summer candidates regional R papers are "
    "normally required, subject to official entry rules. Original practice "
    "should distinguish effects, interpretations, source use and evaluated "
    "judgements as appropriate to the actual selected paper."),
 "Geography": (
    "Pearson Edexcel International GCSE Geography 4XGE1 is the modular "
    "qualification cash-in, requiring 4WGE1 Physical Geography and 4WGE2 "
    "Human Geography. These are distinct assessed units; do not label "
    "the 4XGE1 course as the linear 4GE1 examination. Physical geography "
    "includes coasts, rivers, hazards and fieldwork; Human geography "
    "requires confirmation of selected options and case studies."),
 "Business Studies": (
    "Pearson Edexcel International GCSE Business 4BS1 (2017 route) covers "
    "business activity and influences, people, finance, marketing and "
    "operations. Paper 1 considers small-business contexts; Paper 2 larger "
    "business contexts. Distinguish application to a case, explanation "
    "of effects and evaluated business decision-making. A revised "
    "qualification starts teaching September 2027: do NOT silently "
    "switch the current DBSJP cohort to that new syllabus."),
 "French": (
    "Pearson Edexcel International GCSE French 4FR1. Practise listening, "
    "speaking, reading and writing with controlled vocabulary, grammatical "
    "agreement, tenses, comprehension and idiomatic accuracy. Use relevant "
    "official vocabulary and themes only when approved."),
 "Spanish": (
    "Pearson Edexcel International GCSE Spanish 4SP1. Practise listening, "
    "speaking, reading and writing with accurate conjugation, gender, "
    "agreement and tense control. Do not invent prescribed vocabulary."),
 "Computer Science": (
    "Pearson Edexcel GCSE Computer Science 1CP2 involves computational "
    "thinking, algorithms, data representation, computer systems, networks "
    "and a practical programming assessment. Describe Python examples "
    "accurately but do not claim a single coding solution is mandatory."),
 "Combined Science": (
    "AQA GCSE Combined Science Trilogy 8464 consists of biology, chemistry "
    "and physics with six end-of-course papers, two in each science. "
    "Questions test recall, application, analysis, mathematical skills and "
    "required practical understanding. Distinguish Higher/Foundation "
    "content and omit AQA Separate-only sections such as Space Physics."),
 "Separate Sciences": (
    "Three separate AQA GCSEs: Biology 8461, Chemistry 8462 and Physics "
    "8463. These are NOT the same as the double-award 8464 specification. "
    "Use the selected science discipline and tier; different Separate-only "
    "topics and required practicals may apply."),
 "Psychology": (
    "AQA GCSE Psychology 8182 has Cognition and Behaviour (memory, perception, "
    "development, research methods) and Social Context and Behaviour "
    "(social influence, language thought and communication, brain and "
    "neuropsychology, psychological problems). Distinguish theory, evidence, "
    "scenario application, study evaluation and research-method reasoning."),
 "Drama": (
    "AQA GCSE Drama 8261: understanding drama, devising drama and texts "
    "in practice. Written analysis of set text and live theatre is distinct "
    "from actual assessed practical performance. Never claim Gemini has "
    "watched a student's performance without provided evidence."),
 "Design & Technology": (
    "AQA GCSE Design and Technology 8552 has core technical principles, "
    "specialist technical principles and designing/making principles. "
    "Mathematical/scientific application and the iterative process matter. "
    "Non-exam assessment is supervised and teacher-assessed, not an AI quiz."),
 "Food Preparation & Nutrition": (
    "AQA GCSE Food Preparation and Nutrition 8585 examines food, nutrition "
    "and health; food science; food safety; food choice; food provenance. "
    "Practical skills, hygiene and non-exam assessment are distinct from "
    "short written theory tests. Safety advice must remain conservative."),
 "Fine Art": (
    "AQA GCSE Art and Design Fine Art 8202 develops ideas through "
    "investigation, experimentation, recording, refinement and presenting "
    "responses. Portfolio and externally set assignment cannot be reduced "
    "to fully automated marking."),
 "Photography": (
    "AQA GCSE Art and Design Photography 8206 evaluates technical and "
    "expressive development, source investigations, experimentation "
    "and personal outcomes. Portfolio requires human assessment."),
 "Graphic Communication": (
    "AQA GCSE Art and Design Graphic Communication 8203 values the "
    "development of visual ideas, typography, imagery, communication, "
    "experimenting and reflection. Actual design artefacts need review."),
 "Physical Education": (
    "Pearson Edexcel GCSE Physical Education 1PE0 combines theoretical "
    "content and practical assessment. Fitness, movement, physiology, "
    "psychology and socio-cultural influence are academic learning; "
    "physical performance cannot be validated by text alone."),
 "Music": (
    "Pearson Edexcel GCSE Music 1MU0 involves performance, composition "
    "and appraising/listening, with specified set works. Do not invent "
    "audio excerpts; live performance/composition merits teacher review."),
 "BTEC Information Technology": (
    "Pearson BTEC International Level 2 IT (2022) units include organisational "
    "IT, spreadsheets, networking, programming, digital graphics and "
    "animation, websites, apps and games development, subject to "
    "DBSJP's selected optional units. Criterion-based Pass/Merit/Distinction "
    "assessment must use the exact chosen unit and approved assignment."),
 "BTEC Business Studies": (
    "Pearson BTEC International Level 2 Business (2022) supports sector "
    "knowledge, enterprise, communication and business skills, but the "
    "exact qualification size and selected units must be confirmed "
    "before creating assessed tasks."),
 "BTEC Sport": (
    "Pearson BTEC International Level 2 Sport (2022) may include coaching, "
    "fitness, exercise testing, nutrition and event planning, depending "
    "on the school unit selection. Do not invent unit criteria."),
 "BTEC Performing Arts": (
    "Pearson BTEC International Level 2 Performing Arts (2022) can "
    "include devising, production and performance. Written practice "
    "does not substitute real performance or teacher-marked portfolios."),
 "BTEC Applied Science": (
    "Pearson BTEC International Level 2 Applied Science (2020) combines "
    "science knowledge and applied practical evidence. Confirm qualification "
    "size and chosen units before assigning unit-specific assessment."),
 "BTEC Music": (
    "Pearson BTEC International Level 2 Music (2022) includes optional "
    "performance, composing, recording and collaborative production "
    "skills. Real performance evidence remains outside text-only marking."),
}

def specification_scope(course,topic,area=""):
    """Short approved overview; never implies unit-by-unit verification."""
    name=course.get("name","")
    return (SCOPES.get(name,"")+
        " Source note: course-level outline checked against public awarding-body "
        "pages; local teaching sequence, particular option, tier and exam entry "
        "must be confirmed by DBSJP. Do NOT claim exact syllabus-point or "
        "mark scheme verification from this short overview.").strip()[:1900] if name in SCOPES else ""
