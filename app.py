from html import escape
from pathlib import Path

import streamlit as st

from builder import show_builder
from quiz import QUESTIONS, Question


st.set_page_config(page_title="Study Bloom", page_icon="🌸")
st.html(f"<style>{Path(__file__).with_name('style.css').read_text(encoding='utf-8')}</style>")

state = st.session_state
if "screen" not in state:
    state.screen = "home"
    state.attempt = 0


def start(question_ids: tuple[int, ...]) -> None:
    state.attempt += 1
    state.question_ids = question_ids
    state.answers = {}
    state.position = 0
    state.screen = "quiz"


def start_quiz(title: str, questions: tuple[Question, ...]) -> None:
    state.quiz_title = title
    state.questions = questions
    start(tuple(range(len(questions))))


def save_answer(question_id: int, widget_key: str) -> None:
    state.answers[question_id] = state[widget_key]


def move(step: int) -> None:
    state.position += step


def submit() -> None:
    state.screen = "results"


if state.screen != "builder":
    # Keep the builder inputs when Streamlit removes widgets from the active screen.
    for key in state:
        if key in {
            "builder_title", "builder_source", "builder_notes", "builder_count",
            "builder_style", "builder_language", "builder_focus",
        } or (key.startswith("draft_field_") and not key.endswith("_delete")):
            state[key] = state[key]


with st.container(key="masthead"):
    st.markdown('<p class="brand-mark" aria-hidden="true">✿</p>', unsafe_allow_html=True)
    st.title("Study Bloom")
    st.write("A little practice goes a long way.")

if state.screen == "home":
    with st.container(key="home-card", border=True):
        st.html('<span class="topic-tag">DevOps fundamentals</span>')
        st.header("Sample quiz")
        st.write("Five questions on Git, continuous integration, containers, and more.")
        sample, create = st.columns(2)
        sample.button(
            "Start Sample Quiz",
            type="primary",
            on_click=start_quiz,
            args=("", QUESTIONS),
        )
        create.button("Create Quiz", on_click=lambda: state.update(screen="builder"))

elif state.screen == "builder":
    show_builder(start_quiz)

elif state.screen == "quiz":
    total = len(state.question_ids)
    question_id = state.question_ids[state.position]
    question = state.questions[question_id]
    position = state.position + 1
    if state.quiz_title:
        st.html(f"<h2>{escape(state.quiz_title)}</h2>")
    st.progress(position / total, text=f"Question {position} of {total}")

    with st.container(key="question-card", border=True):
        st.html(f'<span class="topic-tag">{escape(question.topic)}</span>')
        st.html(f"<h2>{escape(question.prompt)}</h2>")
        widget_key = f"answer_{state.attempt}_{question_id}"
        st.radio(
            question.prompt,
            options=range(len(question.options)),
            format_func=question.options.__getitem__,
            index=state.answers.get(question_id),
            label_visibility="collapsed",
            key=widget_key,
            on_change=save_answer,
            args=(question_id, widget_key),
        )

    back, forward = st.columns(2)
    back.button("Back", disabled=position == 1, on_click=move, args=(-1,))
    if position < total:
        forward.button("Next", type="primary", on_click=move, args=(1,))
    else:
        forward.button(
            "Submit Quiz",
            type="primary",
            disabled=len(state.answers) < total,
            on_click=submit,
        )
        if len(state.answers) < total:
            st.caption("Answer every question to submit. Use Back to revisit any you skipped.")

else:
    missed = tuple(
        question_id for question_id in state.question_ids
        if state.answers[question_id] != state.questions[question_id].correct
    )
    total = len(state.question_ids)
    missed_count = len(missed)
    correct_count = total - missed_count
    with st.container(key="results-card", border=True):
        st.header("Quiz results")
        if state.quiz_title:
            st.html(f"<p>{escape(state.quiz_title)}</p>")
        st.html(
            '<div class="results-score">'
            f'<p class="score">{correct_count} / {total}</p>'
            f'<p class="score-detail">{correct_count} correct · {missed_count} to retry</p>'
            '</div>'
        )
        if not missed:
            st.success("✓ Quiz complete! You got every question right.")
        with st.container(key="results-actions"):
            retry, home = st.columns(2) if missed else (None, st)
            if retry is not None:
                mistake_label = "Mistake" if missed_count == 1 else "Mistakes"
                retry.button(
                    f"Retry {missed_count} {mistake_label}",
                    type="primary",
                    on_click=start,
                    args=(missed,),
                )
            home.button("Back to Home", type="secondary", on_click=lambda: state.update(screen="home"))

    for question_id in state.question_ids:
        question = state.questions[question_id]
        selected = state.answers[question_id]
        with st.container(key=f"review-card-{question_id}", border=True):
            st.html(f"<h3>{escape(question.prompt)}</h3>")
            st.html(f"<p><strong>Your answer:</strong> {escape(question.options[selected])}</p>")
            st.html(f'<p class="correct">✓ <strong>Correct</strong> · {escape(question.options[question.correct])}</p>')
            st.html(f"<p>{escape(question.explanation)}</p>")
            if question.source_quote:
                with st.expander("Source quote"):
                    st.html(f'<p class="source-quote">{escape(question.source_quote)}</p>')
