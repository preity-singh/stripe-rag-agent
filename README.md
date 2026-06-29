# Stripe RAG Support Agent

A RAG-powered customer support agent built on Stripe's public documentation. 
Ask questions about payments, webhooks, subscriptions, and billing — 
get answers grounded in real Stripe docs with source citations. 
Unanswerable questions automatically escalate to a Notion support ticket.

## Demo

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
Stripe docs → fetch → chunk → embed → ChromaDB

**Query time** (runs on every question):
User question → embed → semantic search → top 5 chunks → Claude → answer + sources

The key is the semantic search step. Rather than keyword matching, the question 
is converted to a vector and compared against 148 embedded chunks of Stripe 
documentation. Similar meaning maps to nearby vectors — so "why did my charge 
fail" retrieves the declines documentation even though those exact words don't 
appear there.

When Claude can't answer confidently from the retrieved context, it says so 
instead of guessing — and a Notion ticket is automatically created for human 
follow-up.

## Architecture

| Component | Tool | Why |
|-----------|------|-----|
| Embedding model | `all-MiniLM-L6-v2` | Free, runs locally, optimized for semantic similarity |
| Vector database | ChromaDB | Local, persistent, zero setup |
| LLM | Claude Haiku 4.5 | Fast and cost-efficient for support queries |
| UI | Streamlit | Python-native, no frontend code needed |
| Ticket escalation | Notion API | Real integration, visible during demos |

## Features

- **Semantic search** — finds relevant docs by meaning, not keywords
- **Source citations** — every answer includes the Stripe docs pages it used
- **Multi-turn memory** — follow-up questions understand prior context
- **Confidence handling** — says "I don't know" instead of hallucinating
- **Notion escalation** — automatically creates a support ticket for unanswerable questions

## Project Structure

