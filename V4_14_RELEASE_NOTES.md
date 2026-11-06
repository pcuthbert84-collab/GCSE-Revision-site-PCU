# DBSJP Revision Hub V4.14 – Examination Skills + DBSJP Colours

Prepared as a complete GitHub source branch `v4-14-exam-skills-dbsjp-theme`. It builds on the prior V4.13 learning/exam pathways and retains teaching guidance, Gemini fallbacks, Maths, Corbettmaths and Academic Quality Manager.

## User-facing enhancements

**DBSJP branding**
- Navy `#071D59` navigation, red `#D50032` primary buttons, white background and neutral-grey panels, inspired by the supplied DBSJP logo.
- Streamlit theme in `.streamlit/config.toml`, with additional carefully scoped CSS in `app.py`.
- Existing logo display retained. The logo is still loaded from its existing external URL; the uploaded binary logo was **not** embedded in this code release because local binary file operations were unavailable.

**Exam practice**
- Short question (2–8 provisional marks) remains available for every topic.
- History 4HI1: original 16-mark historical judgement; 8-mark two-effects explanation; 6-mark comparison when a Medicine/change topic is identified.
- English Literature 4ET1: original unseen-poetry analysis (20 practice marks) when a matching topic is identified; 30-mark extended text analysis for named literature content. The specific paper or coursework route must be confirmed with the school.
- English Language A 4EA1: original transactional writing task with an **illustrative 30-mark practice scale**, explicitly NOT an official Paper 1 allocation.
- Maths: existing exact/AI question generation is preserved; it does not pretend to represent every official question format.
- Extended generators enforce the chosen mark total, four distinct provisional assessment criteria, and clearly differentiate original tasks from official exam papers. If generation fails, the app does not silently substitute a shorter task.
- For English Literature, published text quotations must not be invented. An unseen poem, if created, must be fully original and supplied in the question.
- For History, no invented historical primary-source quotation or document.

## Academic caveat

These are **exam-style training activities**, not the examination board's exact questions, level descriptors or grading. Gemini's extended-writing marks are indicative and should be moderated by teachers. The UI avoids falsely claiming official scores or verified paper mapping. In UAE settings, Pearson may require regional paper variants; refer to the school's current entry route.

## Files changed

- `app.py`
- `engine/v4_ai.py`
- `engine/exam_modes.py` (new)
- `.streamlit/config.toml` (new)
- `tests/test_exam_modes_v414.py` (new)

## Test and deployment status

Verified all five files exist on the **separate V4.14 branch**, and checked expected UI wiring and code paths by inspecting the repository. The Python execution environment continued to fail with a ClientError, so the new tests and full Streamlit runtime **have not been run** and no unverified 'tests passed' claim is made.

Recommended before production:
1. Download the branch archive and deploy to an isolated Streamlit test app, or run `python -m unittest discover -s tests`.
2. Try a 16-mark History task, an 8-mark two-effects task, an unseen poetry task, and a transactional-writing task; confirm response validation and marking.
3. Check text contrast, sidebar navigation and logo display at mobile widths.
4. Merge into `main` only after the test app passes.

Production `main` was not modified.
