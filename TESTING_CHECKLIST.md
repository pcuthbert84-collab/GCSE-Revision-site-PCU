# DBSJP V4 testing checklist

This release is intended for a **small trusted testing group using anonymised answers**. No student accounts.

## Content
- [ ] All listed Level 2 subjects appear and Level 3 / Arabic / Islamic do not.
- [ ] BTEC Sport uses HYP4, not HPMN7.
- [ ] Maths uses 4MA1, Separate Sciences uses AQA Biology/Chemistry/Physics codes.
- [ ] English Literature set-text / History / Geography teaching blocks reflect DBSJP curriculum.
- [ ] French includes *Qui suis-je ?* while Spanish includes *¡Desconéctate!*; no cross-over.
- [ ] AI-created explanations include genuine, correct subject teaching, worked examples and misconceptions.
- [ ] No AI-generated task quotes or claims to reproduce real copyrighted past-paper items.

## Maths marking
- [ ] Input one complete working sequence into a single box; test percent increase by two methods.
- [ ] Quadratic roots accepted in either order.
- [ ] Valid alternative methods are not rejected merely for differing from the exemplar.
- [ ] Partial method-mark decisions for AI-generated Maths questions are marked as indicative; flag mistaken judgements.
- [ ] Unparseable answers are treated as needing review, not automatically wrong.

## Other subjects
- [ ] Written answers can receive specific improvement points before the model answer is shown.
- [ ] Alternative legitimate science explanations and history interpretations are considered.
- [ ] Low-confidence feedback never issues an authoritative zero.
- [ ] BTEC questions ask about skills, rather than pretending to set or grade a real assignment.

## Workflow
- [ ] Second attempt remains optional.
- [ ] Changing the subject clears any previous question.
- [ ] Next question adapts difficulty after an independently scored attempt.
- [ ] Flag a question with bad content or marking; download testing issues JSON in the sidebar.
- [ ] Without API key, local questions work where present and missing material is clearly labelled.

## Deployment
- [ ] Add Gemini API key only in Streamlit secrets; never GitHub.
- [ ] Ensure the Google Cloud project is on its free tier with paid billing not enabled.
- [ ] Keep the audience to a small testing group, do not send student-identifying data to Gemini.
