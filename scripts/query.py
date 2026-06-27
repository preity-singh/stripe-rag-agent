import streamlit as st

from dotenv import load_dotenv
load_dotenv()  

import anthropic
client = anthropic.Anthropic() 

from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer('all-MiniLM-L6-v2')

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="stripe_docs")

SYSTEM_PROMPT = """You are a helpful Stripe customer support agent.
Use only the provided documentation excerpts to answer the user's question.
Give a clear, direct answer as if you're a knowledgeable support agent — not a list of excerpts.
At the end of your response, include a "Sources:" section with the relevant URLs.
If the provided context doesn't contain enough information to answer confidently,
say "I don't have enough information to answer that accurately" rather than guessing.
Be concise, clear, and accurate."""

# dictionary containing top 5 relevant chunks and their metadata 
# for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
#     print(f"\n--- Chunk {i+1} ---")
#     print(f"Source: {metadata['source']}")
#     print(f"{doc[:200]}...")

# calls claude api to get answer from model using user query and relevant chunks from ChromaDB
def get_answer(user_query, results, conversation_history):
    context = "\n\n".join(
        f"[Source: {metadata['source']}]\n{doc}" for doc, 
        metadata in zip(results['documents'][0], results['metadatas'][0])
    )

    user_message = f"Here is the relevant documentation:\n\n{context}\n\nQuestion: {user_query}"
    
    conversation_history.append({"role": "user", "content": user_message})
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=conversation_history
    )
    answer = response.content[0].text
    conversation_history.append({"role": "assistant", "content": answer})
    return answer

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if __name__ == "__main__": 
    while True:
        user_query = input("Enter your Stripe query: ")
        if user_query.lower() == "quit":
            break

        query_embedding = model.encode(user_query) # Generate embedding for the user query

        # semantic search in ChromaDB 
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=5
        )
            
        answer = get_answer(user_query, results, st.session_state.conversation_history)
        print(answer)