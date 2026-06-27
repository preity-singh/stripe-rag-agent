import streamlit as st
from scripts.query import get_answer, collection, model

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Stripe Customer Support Agent")
query = st.chat_input("What are you curious about?")
    # render chat bubbles
for role, message in st.session_state.messages:
    if role == "user":
        st.chat_message("user").write(message)
    else:
        st.chat_message("assistant").write(message)

if query:
    # embed and retrieve
    query_embedding = model.encode(query)
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=5
    )
    # call get_answer
    answer = get_answer(query, results, st.session_state.conversation_history)
    # append to session state
    st.session_state.messages.append(("user", query))
    st.session_state.messages.append(("assistant", answer))
    st.rerun()

