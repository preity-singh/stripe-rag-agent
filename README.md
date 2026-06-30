# Stripe RAG Support Agent

A RAG-powered customer support agent built on Stripe's public documentation. 
Ask questions about payments, webhooks, subscriptions, and billing — 
get answers grounded in real Stripe docs with source citations. 
Unanswerable questions automatically escalate to a Notion support ticket.

**Deploy branch:** Production-ready with Pinecone cloud vector database and Streamlit Cloud deployment support.

## The Problem

Stripe's documentation is extensive and spread across dozens of pages. Finding 
the right answer means knowing where to look, reading through long guides, and 
piecing together information from multiple sources. This agent lets developers 
ask questions in plain English and get answers grounded directly in Stripe's 
official docs, with source citations so every answer is verifiable, conversation 
memory so follow-up questions work naturally, and automatic escalation to a 
support ticket when the question falls outside the knowledge base.

## How It Works

**Build time** (run once to build the knowledge base): 
Stripe docs → fetch → chunk → embed → Pinecone

**Query time** (runs on every question):
User question → embed → semantic search → top 5 chunks → Claude → answer + sources

The key is the semantic search step. Rather than keyword matching, the question 
is converted to a vector and compared against embedded chunks of Stripe 
documentation stored in Pinecone. Similar meaning maps to nearby vectors — so 
"why did my charge fail" retrieves the declines documentation even though those 
exact words don't appear there.

When Claude can't answer confidently from the retrieved context, it says so 
instead of guessing — and a Notion ticket is automatically created for human 
follow-up.

## Demo

### Multi-turn Conversation with Memory
![Question](assets/SetupWebhooks.png)

![Follow-up with Memory](assets/TestWebhooks.png)

### Handling Non-Stripe Questions
![Non-Stripe Question Handling](assets/IrrelevantQuestion.png)

### Automatic Ticket Escalation
![Ticket Escalation](assets/TicketEscalation.png)
![Notion Ticket](assets/NotionTicket2.png)

## Architecture

| Component | Tool | Why |
|-----------|------|-----|
| Embedding model | `all-MiniLM-L6-v2` | Free, optimized for semantic similarity |
| Vector database | Pinecone | Cloud-hosted, scales automatically, zero maintenance |
| LLM | Claude Haiku 4.5 | Fast and cost-efficient for support queries |
| UI | Streamlit | Python-native, deploys to Streamlit Cloud |
| Ticket escalation | Notion API | Real integration, visible during demos |

## Features

- **Semantic search** — finds relevant docs by meaning, not keywords
- **Source citations** — every answer includes the Stripe docs pages it used
- **Multi-turn memory** — follow-up questions understand prior context
- **Confidence handling** — says "I don't know" instead of hallucinating
- **Notion escalation** — automatically creates a support ticket for unanswerable questions
- **Rate limiting** — 10 questions per session to manage API costs
- **Cloud-ready** — Pinecone vector database for scalable, serverless deployment

## Project Structure

```
stripe-rag-agent/
├── app.py                      # Streamlit chat UI with session state
├── scripts/
│   ├── ingest.py              # Fetch, chunk, embed Stripe docs → Pinecone
│   ├── query.py               # Semantic search + Claude API integration
│   └── notion_ticket.py       # Notion API ticket creation
├── assets/                    # Screenshots for README
├── requirements.txt           # Python dependencies
└── .env                       # API keys (not tracked in git)
```

## Getting Started

### Prerequisites
- Python 3.9+
- Anthropic API key ([get one here](https://console.anthropic.com/))
- Pinecone API key ([get one here](https://www.pinecone.io/))
- Notion API key + Database ID ([setup guide](https://developers.notion.com/docs/create-a-notion-integration))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/preity-singh/stripe-rag-agent.git
   cd stripe-rag-agent
   git checkout deploy
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_key_here
   PINECONE_API_KEY=your_pinecone_key_here
   PINECONE_INDEX_NAME=stripe-docs
   PINECONE_HOST=your_pinecone_host_here
   NOTION_API_KEY=your_notion_key_here
   NOTION_DATABASE_ID=your_database_id_here
   ```
   
   **Pinecone Setup:**
   - Create a free Pinecone account
   - Create a new index named `stripe-docs` with dimension `384` (matches `all-MiniLM-L6-v2`)
   - Copy your API key and index host URL

5. **Build the knowledge base** (run once)
   ```bash
   python scripts/ingest.py
   ```
   This fetches 20 Stripe documentation pages, chunks them, generates embeddings, and stores them in Pinecone. Takes ~1-2 minutes.

6. **Launch the chat UI**
   ```bash
   streamlit run app.py
   ```
   Opens at `http://localhost:8501`

### Usage

**Ask Stripe-related questions:**
- "How do I handle webhooks?"
- "What's the difference between payment intents and charges?"
- "How do I cancel a subscription?"

**Multi-turn conversations work naturally:**
```
You: How do I test subscriptions?
Agent: [explains with test card numbers]
You: What about failed payments?
Agent: [continues in context of subscription testing]
```

**Out-of-scope questions:**
The agent will politely redirect you if you ask non-Stripe questions (e.g., "What's the weather?") and explain its capabilities.

**Uncertain answers:**
When the agent can't answer confidently from the docs, it says "I don't have enough information" and a Notion ticket is auto-created for escalation.

### Alternative: CLI Mode

Run queries from the command line:
```bash
python scripts/query.py
```

## Deployment

### Deploy to Streamlit Cloud

1. **Push to GitHub**
   ```bash
   git push origin deploy
   ```

2. **Connect to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app" → select your repository and `deploy` branch
   - Set main file path to `app.py`

3. **Add secrets in Streamlit Cloud**
   
   In your app settings, add these secrets:
   ```toml
   ANTHROPIC_API_KEY = "your_anthropic_key_here"
   PINECONE_API_KEY = "your_pinecone_key_here"
   PINECONE_INDEX_NAME = "stripe-docs"
   PINECONE_HOST = "your_pinecone_host_here"
   NOTION_API_KEY = "your_notion_key_here"
   NOTION_DATABASE_ID = "your_database_id_here"
   ```

4. **Deploy**
   
   Streamlit Cloud will automatically deploy your app. Any push to the `deploy` branch triggers a redeployment.

**Note:** Make sure to run `python scripts/ingest.py` locally first to populate your Pinecone index before deploying. The deployed app reads from Pinecone but doesn't run the ingestion script.

