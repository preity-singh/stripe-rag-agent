import streamlit as st
from scripts.query import get_answer, index, model
from scripts.notion_ticket import create_notion_ticket

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

st.title("Stripe Customer Support Agent")
query = st.chat_input("What are you curious about?")
    # render chat bubbles
for role, message in st.session_state.messages:
    if role == "user":
        st.chat_message("user").write(message)
    else:
        st.chat_message("assistant").write(message)

if query:
    # check rate limit
    if st.session_state.question_count >= 10:
        st.session_state.messages.append(("user", query))
        st.session_state.messages.append(("assistant", "You've reached the question limit for this session (10/10). Please refresh the page to start a new session."))
        st.rerun()
    else:
        # embed and retrieve
        query_embedding = model.encode(query)
        results = index.query(
            vector=query_embedding.tolist(),
            top_k=5,
            include_metadata=True
        )
        # call get_answer
        answer = get_answer(query, results, st.session_state.conversation_history)

        # check for escalation flag
        should_escalate = answer.startswith("[ESCALATE]")
        if should_escalate:
            answer = answer.replace("[ESCALATE]", "").strip()

        # append to session state
        st.session_state.messages.append(("user", query))
        st.session_state.messages.append(("assistant", answer))

        # increment question counter
        st.session_state.question_count += 1

        # ticket creation logic - only for Stripe-related questions that need escalation
        if should_escalate:
            create_notion_ticket(query)
            st.session_state.messages.append(("assistant", "A support ticket has been created for your query. Our team will get back to you shortly."))

        st.rerun()