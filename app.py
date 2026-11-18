
import streamlit as st
from rag.chat import ask_question_stream

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="DarGlobal × Wasalt AI",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -1px;
    }

    .subtitle {
        color: #8B8B8B;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    .source-card {
        padding: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 10px;
        margin-bottom: 8px;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.title("DarGlobal × Wasalt")
    st.caption("AI Knowledge Assistant")

    st.divider()

    st.subheader("About")
    st.write(
        "Ask questions about DarGlobal's real estate "
        "developments and Wasalt's PropTech platform."
    )

    st.divider()

    st.subheader("Capabilities")
    st.markdown("""
    - Company information
    - Project information
    - Property platform services
    - Company comparison
    - Source-backed answers
    """)

    st.divider()

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Powered by RAG, ChromaDB and OpenRouter")

# ---------------- SESSION STATE ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- HEADER ----------------

st.markdown(
    '<div class="main-title">DarGlobal × Wasalt AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'An intelligent assistant for real estate knowledge and company insights.'
    '</div>',
    unsafe_allow_html=True
)

# ---------------- EXAMPLE QUESTIONS ----------------

if not st.session_state.messages:
    st.subheader("Explore the knowledge base")

    examples = [
        "What is DarGlobal's development portfolio?",
        "What services does Wasalt offer?",
        "Tell me about the Rayana project.",
        "Compare DarGlobal and Wasalt."
    ]

    columns = st.columns(2)

    for index, example in enumerate(examples):
        with columns[index % 2]:
            if st.button(
                example,
                key=f"example_{index}",
                use_container_width=True
            ):
                st.session_state.pending_question = example
                st.rerun()

# ---------------- DISPLAY CHAT HISTORY ----------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":

            sources = message.get("sources", [])

            if sources:
                with st.expander("View sources"):
                    for source in sources:
                        st.markdown(
                            f"**{source['source']}** — "
                            f"{source['title']}"
                        )
                        st.markdown(
                            f"[Open source]({source['url']})"
                        )

            diagnostics = message.get("diagnostics")

            if diagnostics:
                with st.expander("Retrieval diagnostics"):
                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Query type",
                        diagnostics["query_type"]
                    )

                    col2.metric(
                        "Retrieved chunks",
                        diagnostics["retrieved_count"]
                    )

                    col3.metric(
                        "Relevant chunks",
                        diagnostics["relevant_count"]
                    )

# ---------------- USER INPUT ----------------

prompt = st.chat_input(
    "Ask something about DarGlobal or Wasalt..."
)

if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")


# ---------------- PROCESS QUESTION ----------------

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        try:
            # Step 1: Retrieve evidence and prepare stream.
            with st.spinner("Searching knowledge base..."):
                conversation_history = st.session_state.messages[:-1]

                result = ask_question_stream(
                    question=prompt,
                    conversation_history=conversation_history
                )

            # Step 2: Display generated tokens progressively.
            answer = st.write_stream(result["stream"])

            if not answer:
                raise RuntimeError("The AI returned an empty response.")

            sources = result.get("sources", [])

            # Step 3: Display sources.
            if sources:
                with st.expander("View sources"):
                    for source in sources:
                        st.markdown(
                            f"**{source['source']}** — "
                            f"{source['title']}"
                        )

                        st.markdown(
                            f"[Open source]({source['url']})"
                        )

            # Step 4: Display retrieval diagnostics.
            with st.expander("Retrieval diagnostics"):
                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Query type",
                    result["query_type"]
                )

                col2.metric(
                    "Retrieved chunks",
                    result["retrieved_count"]
                )

                col3.metric(
                    "Relevant chunks",
                    result["relevant_count"]
                )

            # Step 5: Save completed response.
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "diagnostics": {
                    "query_type": result["query_type"],
                    "retrieved_count": result["retrieved_count"],
                    "relevant_count": result["relevant_count"]
                }
            })

        except Exception as error:
            error_message = (
                "Something went wrong while processing your question. "
                "Please try again."
            )

            st.error(error_message)

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message,
                "sources": [],
                "diagnostics": None
            })

            print(
                f"[APP ERROR] {type(error).__name__}: {error}"
            )
