# DBSJP Revision Hub — Mathematics Prototype (V1)

**Course:** Pearson Edexcel International GCSE Mathematics A, 4MA1, **Higher Tier** (linear papers 1H and 2H).

This is a free-first working prototype, not a finished school deployment. No API key is needed.

## What works

- Navigate all six course areas and their topic headings; four specific skills are active: quadratic factorisation, quadratic formula, percentage change, and ratio sharing.
- Review short original teaching summaries and worked examples.
- Generate fresh *original* parameterised maths questions.
- Enter working separately and final numerical answers; exact answers checked using SymPy.
- Receive feedback, try again (optional), reveal a worked solution, and adapt the next question's difficulty.
- View progress by topic/skill, with an expanded detail view; export and restore JSON progress.
- Open the Pearson qualification page for verified past-paper routes.

**Important limitation:** Current marking tests whether the **final numerical answer** is correct. It does **not** yet assign method marks, or reliably mark mathematical working. Correct final answers receive a provisional full-answer score only, and should not be interpreted as an official Pearson mark. It does not use AI yet. The wording "AI" is intentionally absent from the active question screens.

**Progress is session-only.** Closing/restarting the server, deployment, browser session loss, or memory recycling may erase it; download a JSON copy before leaving. This is not a multi-user app and does not have secure authentication. Do not enter personally identifying student information.

## Run locally

1. Install Python 3.11+.
2. In this folder, run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy for £0 with Streamlit Community Cloud

1. Create a **private** repository on GitHub and upload the files in this folder (preserve the structure).
2. Visit https://share.streamlit.io and sign in with GitHub.
3. Create an app from the repository; main file: `app.py`.
4. Select Python 3.12 or another supported version and deploy.
5. Keep the app **private/invite-restricted** if you will share it. The prototype itself has **no student login or privacy guarantees**.

Streamlit Community Cloud may require additional permissions to deploy a private repository. Do not put keys or student personal data in the repository.

## Design roadmap (not yet implemented)

1. Manually reviewed complete skill map, official content sources, revision materials and resources.
2. Optional pluggable free-tier AI generation/feedback service, non-identifying prompts, strict specification mapping, mathematical validation, free-quota fail-closed controls. Privacy review required before processing children's answers.
3. SymPy method checks for supported algebra, more sophisticated marking rubrics and review of errors.
4. Invitation-only registration, role-based student/parent/admin permissions and persistent progress using an appropriately secured hosted database. Never rely solely on hiding Streamlit pages for access control.
5. Official past-paper mode with source links, not unauthorised reproduction of Pearson questions.
6. Additional subjects.

## Sources

- [Pearson official Mathematics A qualification page](https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses/international-gcse-mathematics-a-2016.html)
- DBSJP Key Stage 4 Options Booklet 2026–2027 (user supplied).

Course headings are for navigation and require detailed teacher verification before wider rollout. Original questions are not asserted to be official past-paper questions.
