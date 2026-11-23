from io import BytesIO

import streamlit as st
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from generation import generate_questions, validate_question
from quiz import Question


def read_pdf(upload):
    try:
        reader = PdfReader(BytesIO(upload.getvalue()))
        if reader.is_encrypted:
            st.error("This PDF is password-protected. Upload an unlocked copy or paste the notes below.")
            return
        page_count = len(reader.pages)
        if page_count == 0:
            st.warning("This PDF has no pages. Paste your notes below.")
            return
        first, last = (1, 1)
        if page_count > 1:
            first, last = st.slider(
                "Page range", 1, page_count, (1, page_count), key="builder_page_range"
            )
        else:
            st.caption("Page 1 of 1")
        if st.button("Extract Text"):
            pages = (reader.pages[index].extract_text() or "" for index in range(first - 1, last))
            notes = "\n\n".join(page.strip() for page in pages if page.strip())
            if any(char.isalnum() for char in notes):
                st.session_state.builder_notes = notes
                st.session_state.pdf_message = ("success", f"Imported pages {first}–{last} into the notes preview.")
            else:
                st.session_state.pdf_message = (
                    "warning", "These pages have no usable text and may be scanned. Paste your notes into the preview below."
                )
    except (PyPdfError, OSError, ValueError, RecursionError):
        st.session_state.pdf_message = ("error", "Could not read this PDF. Try another file or paste your notes below.")
    if message := st.session_state.get("pdf_message"):
        level, content = message
        getattr(st, level)(content)


def reset_pdf():
    st.session_state.pop("pdf_message", None)
    st.session_state.pop("builder_page_range", None)


def show_builder(start_quiz):
    state = st.session_state
    with st.container(key="builder-card", border=True):
        st.header("Create Quiz")
        title = st.text_input("Quiz title", key="builder_title")
        source = st.radio(
            "Notes source", ("Paste Notes", "Upload PDF"), horizontal=True, key="builder_source"
        )
        if source == "Upload PDF":
            upload = st.file_uploader("Upload PDF", type="pdf", key="builder_file", on_change=reset_pdf)
            if upload is not None:
                read_pdf(upload)
        notes = st.text_area("Notes preview", height=220, key="builder_notes",
                             placeholder="Paste your notes here, or import text from a PDF.")

        st.subheader("Quiz options")
        count = st.selectbox("Number of questions", (5, 10, 15), key="builder_count")
        style = st.selectbox("Style", ("Recall", "Scenario-based", "Mixed"), index=2, key="builder_style")
        language = st.selectbox("Language", ("English", "Bahasa Indonesia"), key="builder_language")
        focus = st.text_input("Focus topic (optional)", key="builder_focus")
        st.caption("Generate Quiz sends the notes preview and quiz options to Gemini.")
        if st.button("Generate Quiz", type="primary"):
            if not title.strip() or not notes.strip():
                st.error("Enter a quiz title and add notes to the preview.")
            else:
                try:
                    with st.spinner("Generating questions from your notes…"):
                        questions = generate_questions(notes, count, style, language, focus.strip())
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    if questions:
                        state.generated_count = len(questions)
                        state.requested_count = count
                        state.draft = dict(enumerate(questions))
                        state.draft_notes = notes
                        state.draft_version = state.get("draft_version", 0) + 1
                    else:
                        st.warning("Generated 0 questions. Try adding more detail to your notes or broadening the focus topic.")

    if state.get("draft"):
        review_draft(title, start_quiz)
    elif "draft" in state:
        st.info("All draft questions were deleted. Generate another quiz to continue.")
    st.button("Back to Home", on_click=lambda: state.update(screen="home"))


def delete_question(question_id):
    st.session_state.draft.pop(question_id)


def review_draft(title, start_quiz):
    state = st.session_state
    st.header("Review draft")
    if state.generated_count:
        st.info(f"Generated {state.generated_count} of {state.requested_count} requested questions.")
    st.caption("Edit the fields below or delete questions before starting. Source quotes must match the notes used to generate this draft.")
    edited = []
    for number, (question_id, question) in enumerate(state.draft.items(), 1):
        key = f"draft_field_{state.draft_version}_{question_id}"
        with st.expander(f"Question {number} · {question.prompt}", expanded=number == 1):
            topic = st.text_input("Topic", question.topic, key=f"{key}_topic")
            prompt = st.text_area("Question", question.prompt, key=f"{key}_prompt")
            options = tuple(
                st.text_input(f"Choice {index + 1}", option, key=f"{key}_option_{index}")
                for index, option in enumerate(question.options)
            )
            correct = st.selectbox(
                "Correct answer", range(4), index=question.correct,
                format_func=lambda index: f"Choice {index + 1}", key=f"{key}_correct",
            )
            explanation = st.text_area("Explanation", question.explanation, key=f"{key}_explanation")
            quote = st.text_area("Source quote", question.source_quote, key=f"{key}_quote")
            st.button("Delete question", key=f"{key}_delete", on_click=delete_question, args=(question_id,))
            edited.append(Question(topic, prompt, options, correct, explanation, quote))

    if st.button("Start Quiz", type="primary"):
        if not title.strip():
            st.error("Enter a quiz title before starting.")
            return
        validated = []
        for number, question in enumerate(edited, 1):
            try:
                validated.append(validate_question(question, state.draft_notes))
            except ValueError as exc:
                st.error(f"Question {number} — {exc}")
        if len(validated) == len(edited):
            start_quiz(title.strip(), tuple(validated))
            st.rerun()
