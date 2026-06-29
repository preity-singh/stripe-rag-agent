import requests
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

model = SentenceTransformer('all-MiniLM-L6-v2')

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))

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

vectors_to_upsert = []
for i, (chunk, url) in enumerate(all_chunks):
    embedding = model.encode(chunk) # generate embedding for each chunk
    vectors_to_upsert.append({
        "id": f"chunk_{i}",
        "values": embedding.tolist(),
        "metadata": {"source": url, "text": chunk}
    })

# Upsert in batches of 100 (Pinecone best practice)
batch_size = 100
for i in range(0, len(vectors_to_upsert), batch_size):
    batch = vectors_to_upsert[i:i + batch_size]
    index.upsert(vectors=batch)

print(f"Done. {len(all_chunks)} chunks stored in Pinecone.")
