"""
Chat interface component — renders conversation history and input form.
"""
import streamlit as st
from frontend.components.api_client import chat as api_chat


def render_chat_history(history: list) -> str:
    """Render full chat history as HTML."""
    if not history:
        return ""

    html = '<div style="background:#13131f;border:1px solid #1e1e30;border-radius:16px;padding:20px;margin:12px 0;max-height:400px;overflow-y:auto">'
    for msg in history:
        role    = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "user":
            html += f"""
            <div style="background:rgba(0,200,150,0.08);border:1px solid rgba(0,200,150,0.2);
                        border-radius:12px 12px 4px 12px;padding:10px 14px;
                        margin:8px 0 8px 40px">
              <div style="font-family:DM Mono,monospace;font-size:10px;
                          color:#00C896;letter-spacing:1px;margin-bottom:4px">YOU</div>
              <div style="font-size:14px;color:#F0F0F8">{content}</div>
            </div>"""
        else:
            html += f"""
            <div style="background:#0f0f1a;border:1px solid #1e1e30;
                        border-radius:12px 12px 12px 4px;padding:10px 14px;
                        margin:8px 40px 8px 0">
              <div style="font-family:DM Mono,monospace;font-size:10px;
                          color:#3B82F6;letter-spacing:1px;margin-bottom:4px">NEIGHBORIQ</div>
              <div style="font-size:14px;color:#8888AA;line-height:1.6">{content}</div>
            </div>"""
    html += "</div>"
    return html


def render_suggested_questions(questions: list, key_prefix: str = "sq") -> str | None:
    """
    Render suggested question buttons. Returns the clicked question text or None.
    """
    cols = st.columns(len(questions))
    for i, (col, q) in enumerate(zip(cols, questions)):
        with col:
            if st.button(q, key=f"{key_prefix}_{i}",
                         help=q,
                         use_container_width=True):
                return q
    return None


def render_chat_input(result: dict, key_suffix: str = "main") -> None:
    """
    Full self-contained chat widget — history display + input form.
    Reads/writes st.session_state["chat_history"].
    """
    history = st.session_state.get("chat_history", [])

    # Suggested questions
    st.markdown(
        '<div style="font-family:DM Mono,monospace;font-size:10px;'
        'color:#44445A;letter-spacing:1px;margin-bottom:8px">SUGGESTED QUESTIONS</div>',
        unsafe_allow_html=True,
    )

    questions = [
        "Is this good for first-time buyers?",
        "What are the biggest risks?",
        "Compare to city average",
        "Best streets to target?",
    ]
    clicked = render_suggested_questions(questions, key_prefix=f"cq_{key_suffix}")
    if clicked:
        st.session_state["pending_question"] = clicked

    # History
    if history:
        st.markdown(render_chat_history(history), unsafe_allow_html=True)

    # Input form
    with st.form(key=f"chat_form_{key_suffix}", clear_on_submit=True):
        user_q = st.text_input(
            "Ask anything",
            value=st.session_state.pop("pending_question", ""),
            placeholder="e.g. Is this a good market for investors?",
            label_visibility="collapsed",
            key=f"chat_input_{key_suffix}",
        )
        submitted = st.form_submit_button("Ask →")

    if submitted and user_q and result:
        with st.spinner("Thinking..."):
            resp = api_chat(user_q, result, history)
            st.session_state["chat_history"] = resp.get("chat_history", [])
            st.rerun()