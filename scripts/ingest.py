import requests

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

def fetch_page(url):
    try:
        response = requests.get(url)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def chunk_text(text, chunk_size=500, overlap = 50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks

pages = []
for url in URLS:
    result = fetch_page(url) # store what comes back
    if result:
        # print(f"Fetched {url} — {len(result)} characters") # verify fetch_page works
        chunks = chunk_text(result) 
        pages.extend(chunks)
        print(f"Total chunks: {len(pages)}") # verify chunk_text works
        print(f"\nFirst chunk preview:\n{pages[0]}")
        

