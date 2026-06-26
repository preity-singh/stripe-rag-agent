import requests
from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer('all-MiniLM-L6-v2')

chroma_client = chromadb.PersistentClient(path="./chroma_db")

# TODO: Remove this delete logic later - only needed during development to avoid "already exists" errors
try:
    chroma_client.delete_collection(name="stripe_docs")
except:
    pass

collection = chroma_client.create_collection(name="stripe_docs")

URLS= [
    "https://docs.stripe.com/payments/balances.md",
    "https://docs.stripe.com/payments/payment-intents.md",
    "https://docs.stripe.com/webhooks.md",
    "https://docs.stripe.com/webhooks/handling-payment-events.md",
    "https://docs.stripe.com/billing/subscriptions/design-an-integration.md",
    "https://docs.stripe.com/billing/subscriptions/cancel.md",
    "https://docs.stripe.com/billing/customer.md",
    "https://docs.stripe.com/invoicing/overview.md",
    "https://docs.stripe.com/invoicing/integration.md",
    "https://docs.stripe.com/billing/testing.md",
    "https://docs.stripe.com/error-codes.md",
    "https://docs.stripe.com/keys.md",
    "https://docs.stripe.com/declines.md",
    "https://docs.stripe.com/refunds.md",
    "https://docs.stripe.com/disputes/how-disputes-work.md",
    "https://docs.stripe.com/testing.md",
    "https://docs.stripe.com/connect/how-connect-works.md",
    "https://docs.stripe.com/billing/subscriptions/overview.md",
    "https://docs.stripe.com/radar/rules/reference.md",
    "https://docs.stripe.com/disputes/responding.md"
]

# fetches content from URL
def fetch_page(url):
    try:
        response = requests.get(url)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    
# splits text into chunks with overlap
def chunk_text(text, chunk_size=500, overlap = 50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks

all_chunks = [] # stores all chunks
for url in URLS:
    result = fetch_page(url) # store what comes back
    if result:
        # print(f"Fetched {url} — {len(result)} characters") # verify fetch_page works
        chunks = chunk_text(result) 
        all_chunks.extend([(chunk, url) for chunk in chunks])
        print(f"{url} → {len(chunks)} chunks")
        # print(f"Total chunks: {len(all_chunks)}") # verify chunk_text works

for i, (chunk, url) in enumerate(all_chunks):
    embedding = model.encode(chunk) # generate embedding for each chunk
    collection.add( # add the chunk and its embedding to the ChromaDB collection
        ids=[f"chunk_{i}"], 
        documents=[chunk], 
        metadatas=[{"source": url}], 
        embeddings=[embedding.tolist()]
    )

print(f"Done. {collection.count()} chunks stored in Chroma.") # verify embeddings are stored in ChromaDB
