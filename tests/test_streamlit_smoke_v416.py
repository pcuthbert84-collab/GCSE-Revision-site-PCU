"""Headless Streamlit startup checks: no real student data or Gemini requests."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_revision_hub_initial_page_renders():
    root=Path(__file__).resolve().parents[1]
    app=AppTest.from_file(str(root/"app.py"),default_timeout=30)
    app.run()
    assert not app.exception, "Streamlit threw an exception while rendering the student home page"
    assert app.selectbox, "Student subject selector did not render"
    assert app.radio, "Expected navigation or learning pathway selection"

