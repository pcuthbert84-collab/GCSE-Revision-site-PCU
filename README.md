# DBSJP Revision Hub — V3 (Content-first)

This version deliberately focuses **only** on students selecting a subject and topic, revising useful content and practising one question at a time. **No student accounts or progress dashboards** are included.

## What is ready

- Catalogue of 28 DBSJP subject pathways based on the school's options booklet.
- 14 original, editorially written topic revision modules across 11+ subject areas, including unseen poetry, science, geography, history, business, psychology and computer science.
- Four original Mathematics question generators with SymPy final-answer verification, using confirmed Pearson Edexcel International GCSE Mathematics A (4MA1), Higher Tier.
- Topic-specific practice questions with model answers, hints and an optional second attempt.
- Optional Google Gemini API support to generate original questions and give indicative feedback; it is **not needed** to use the offline content.
- Links to official exam board websites for past-paper access. We **do not** copy or upload copyrighted past-paper questions to AI.

## Scope and honesty

Course index entries are not all equivalent to fully mapped official specifications. Only DBSJP Mathematics 4MA1 is confirmed directly by the user. Some course identifiers come from the options booklet or previous checking, and others remain provisional. Detailed reviewed learning notes are only shown on prepared topics. Other topics clearly show that content is not yet prepared. Non-mathematics offline questions use **self-assessment**, not automated grades. The pilot does not store student answers or progress between sessions.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publish via GitHub + Streamlit Community Cloud

Unzip the archive, upload the **contents** of `dbsjp_revision_hub` to the root of your existing GitHub repo (or a new **private** repo). Point Streamlit to `app.py`. Keep the `.streamlit/config.toml` file and folder structure intact. No database or paid service is required.

## Optional AI configuration

For a developer-only demo with no student identifying information, add the following in Streamlit's **App settings → Secrets**:

```toml
GEMINI_API_KEY = "YOUR_KEY"
GEMINI_MODEL = "gemini-2.5-flash-lite"
```

Do not commit any API keys to GitHub. Check the provider's current free quota and data-use terms before enabling requests with minor students. There is no automatic paid fallback or billing feature built into the application. AI can make mistakes: all AI marks are labelled indicative. Availability of a free tier or quota is not guaranteed by the app.

## Test

From the repository root:

```bash
python -m pytest -q
```

Suggested manual checks:

1. English Literature → Poetry → Unseen poetry → Revise. Confirm detailed guidance and an original worked example.
2. Switch to Test myself, submit an answer and observe self-assessment guidance, second attempt and model answer.
3. Mathematics → topic Quadratic equations → factorising → Test myself. Check that a correct final answer is recognised and a different question is available after completing.
4. Select a topic without prepared notes. It must explicitly say it isn't yet available, not present generic instructions as revision.
5. Check all links and the optional API against current provider terms before sharing with students.


## V3.1 — Fairer mathematics answer assessment
- Checks mathematically equivalent numerical final answers and accepts quadratic roots in either order.
- Accepts `x = -2, x = 3`, fractions/arithmetic, AED suffixes, and Ali/Sara labels in the final-answer field.
- Never compares submitted working text with one exemplar method or marks an unparseable answer as wrong.
- Clearly distinguishes prototype final-answer checks from method marks.
- Correct first attempts let students continue immediately.
- **Limitation:** Arbitrary working is not independently validated or awarded method marks. Full credit is a prototype *answer-check score*, not an official 4MA1 mark scheme.

### V3.2 marking improvement
For one-number Mathematics questions, students may enter complete arithmetic working into the answer box or the working box, including `80 x 0.2 = 16` followed by `80 + 16 = 96`. The arithmetic equalities are verified before extracting the final value. This is not a comprehensive method-marking engine; algebraic/prose methods still need further validation.
