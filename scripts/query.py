from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer('all-MiniLM-L6-v2')

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="stripe_docs")

user_query = input("Enter your Stripe query: ")

# Generate embedding for the user query
query_embedding = model.encode(user_query)

# semantic search in ChromaDB 
results = collection.query(
    query_embeddings=[query_embedding.tolist()],
    n_results=5
)

# dictionary containing top 5 relevant chunks and their metadata 
for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    print(f"\n--- Chunk {i+1} ---")
    print(f"Source: {metadata['source']}")
    print(f"{doc[:200]}...")