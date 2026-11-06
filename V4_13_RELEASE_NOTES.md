# DBSJP Revision Hub V4.13 — Learning + Examination Preparation

## Design principle
The hub supports two equal routes on the same selected DBSJP Level 2 topic.

**Learn the topic:** explanation or teacher-reviewed local notes → worked example → independent retrieval checks → student self-reflection → proceed to exam practice.

**Exam practice:** original 2–8 mark practice task → provisional feedback → optional second attempt → model explanation → suggested next step (return to learning, improve, or increase challenge).

The topic/subject/tier stay selected when switching routes. No student sign-in, personal data collection, paid endpoints or persistent progress database were added.

## Changes
- `app.py`: two prominent study routes, formative learning-check interface, quick link to exam practice, recommendation after practice based on first attempt.
- `engine/learning_path.py`: robust extraction of retrieval checks and conservative post-practice recommendations (uncertain results cannot count as mastery).
- `tests/test_learning_path_v413.py`: unit tests for the new decision functions.
- Existing V4.12 branding, V4.11 teaching knowledge, Corbettmaths, the Maths engines, Gemini fallbacks and Academic Quality Manager retained.

## Academic boundaries
- Retrieval checks are **self-assessed**, not automatically graded.
- The existing AI original-question generator permits **2–8 marks**; no claim of official 16-mark exam simulation.
- Extended-answer marks remain **indicative**; original questions are not published past papers.
- An uncertain or unavailable mark always recommends review rather than automatic promotion.
- Real exam-format alignment, specification audit and teacher-calibrated marking remain future work.

## Release safety
This version was created on the isolated GitHub branch `v4-13-balanced-learning-exam`, not on production `main`.
Source/branch integration checks were performed. Python and Streamlit runtime tests could not be executed because the local execution environment returned ClientError. The new unit tests are included but are **not claimed to have passed**.
Run `python -m unittest discover -s tests` and smoke-test both routes in Streamlit before deploying.
