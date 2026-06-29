import streamlit as st
from scripts.query import get_answer, index, model
from scripts.notion_ticket import create_notion_ticket

# Page config
st.set_page_config(
    page_title="Stripe Support Agent",
    page_icon="💳",
    layout="wide"
)

# Custom CSS for sleek styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stSidebar {
        background-color: #ffffff;
    }
    h1 {
        color: #635bff;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .topic-item {
        background-color: #f3f4f6;
        padding: 8px 12px;
        border-radius: 6px;
        margin: 6px 0;
        font-size: 0.9rem;
        color: #374151;
    }
    .counter-box {
        background: linear-gradient(135deg, #635bff 0%, #4f46e5 100%);
        color: white;
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(99, 91, 255, 0.2);
    }
    .counter-number {
        font-size: 2rem;
        font-weight: bold;
        margin: 8px 0;
    }
    .counter-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

# Sidebar
with st.sidebar:
    st.markdown("## 💳 Stripe Support Agent")
    st.markdown("Get instant answers from Stripe's official documentation.")

    # Question counter
    remaining = 10 - st.session_state.question_count
    st.markdown(f"""
        <div class="counter-box">
            <div class="counter-label">Questions Remaining</div>
            <div class="counter-number">{remaining}/10</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 📚 Topics I Know About")
    topics = [
        "💰 Payments & Charges",
        "🔔 Webhooks & Events",
        "🔄 Subscriptions & Billing",
        "👤 Customer Management",
        "🧾 Invoicing",
        "🧪 Testing & Test Mode",
        "❌ Refunds & Cancellations",
        "⚠️ Disputes & Chargebacks",
        "🔑 API Keys & Authentication",
        "📉 Declined Payments",
        "🔗 Stripe Connect",
        "🛡️ Radar & Fraud Prevention"
    ]

    for topic in topics:
        st.markdown(f'<div class="topic-item">{topic}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("💡 **Tip:** Ask follow-up questions — I remember our conversation!")

# Main content
st.title("Stripe Customer Support Agent")
st.markdown('<p class="subtitle">Ask me anything about Stripe payments, webhooks, subscriptions, and more.</p>', unsafe_allow_html=True)

# Render chat messages
for role, message in st.session_state.messages:
    if role == "user":
        st.chat_message("user").write(message)
    else:
        st.chat_message("assistant").write(message)

# Chat input
query = st.chat_input("Ask me about Stripe... (e.g., How do I handle webhooks?)")

if query:
    # Check rate limit
    if st.session_state.question_count >= 10:
        st.session_state.messages.append(("user", query))
        st.session_state.messages.append(("assistant", "You've reached the question limit for this session (10/10). Please refresh the page to start a new session."))
        st.rerun()
    else:
        # Embed and retrieve
        query_embedding = model.encode(query)
        results = index.query(
            vector=query_embedding.tolist(),
            top_k=5,
            include_metadata=True
        )
        # Call get_answer
        answer = get_answer(query, results, st.session_state.conversation_history)

        # Check for escalation flag
        should_escalate = answer.startswith("[ESCALATE]")
        if should_escalate:
            answer = answer.replace("[ESCALATE]", "").strip()

        # Append to session state
        st.session_state.messages.append(("user", query))
        st.session_state.messages.append(("assistant", answer))

        # Increment question counter
        st.session_state.question_count += 1

        # Ticket creation logic - only for Stripe-related questions that need escalation
        if should_escalate:
            create_notion_ticket(query)
            st.session_state.messages.append(("assistant", "A support ticket has been created for your query. Our team will get back to you shortly."))

        st.rerun()
