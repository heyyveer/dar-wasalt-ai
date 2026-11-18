
import re

from rag.retrieval import retrieve
from rag.query_router import (
    classify_source,
    expand_retrieval_query,
    is_out_of_domain_query
)
from chatbot.llm import (
    generate_answer,
    generate_answer_stream,
    rewrite_follow_up_question
)


MAX_DISTANCE = 0.70
COMPARISON_MAX_DISTANCE = 0.72

TOP_K = 5
COMPARISON_TOP_K = 3

MAX_HISTORY_MESSAGES = 6

NO_INFORMATION_MESSAGE = (
    "I couldn't find sufficient relevant information "
    "in the available knowledge base."
)

OUT_OF_DOMAIN_MESSAGE = (
    "I'm designed to answer questions about DarGlobal, Wasalt, "
    "their real estate projects, services, and related property "
    "information. Please ask me something related to these topics."
)


FOLLOW_UP_PATTERNS = [
    r"\bit\b",
    r"\bits\b",
    r"\bthey\b",
    r"\bthem\b",
    r"\btheir\b",
    r"\bthere\b",
    r"\bthis project\b",
    r"\bthat project\b",
    r"\bthis company\b",
    r"\bthat company\b",
    r"\bwhat about\b",
    r"\band what\b",
    r"\bhow about\b",
    r"\bwho is the contractor\b",
    r"\bwhere is it\b",
    r"\bwhen was it\b",
    r"\bhow much\b"
]


def is_comparison_query(question):
    normalized = question.lower()

    comparison_keywords = [
        "compare",
        "comparison",
        "difference",
        "differences",
        "versus",
        " vs "
    ]

    mentions_darglobal = (
        "darglobal" in normalized
        or "dar global" in normalized
    )

    mentions_wasalt = "wasalt" in normalized

    asks_comparison = any(
        keyword in normalized
        for keyword in comparison_keywords
    )

    return (
        mentions_darglobal
        and mentions_wasalt
        and asks_comparison
    )


def is_follow_up_question(question):
    normalized = question.lower().strip()

    if any(
        re.search(pattern, normalized)
        for pattern in FOLLOW_UP_PATTERNS
    ):
        return True

    # Short questions often depend on previous context.
    if (
        len(normalized.split()) <= 5
        and classify_source(normalized) is None
    ):
        return True

    return False


def get_recent_history(conversation_history):
    if not conversation_history:
        return []

    return conversation_history[-MAX_HISTORY_MESSAGES:]


def resolve_question(question, conversation_history):
    """
    Rewrite only context-dependent questions.
    Standalone questions avoid an additional LLM request.
    """

    history = get_recent_history(conversation_history)

    if not history:
        return question

    if not is_follow_up_question(question):
        return question

    rewritten_question = rewrite_follow_up_question(
        question=question,
        conversation_history=history
    )

    return rewritten_question or question


def retrieve_comparison_results(question):
    darglobal_query = expand_retrieval_query(
        question,
        source="DarGlobal"
    )

    wasalt_query = expand_retrieval_query(
        question,
        source="Wasalt"
    )

    darglobal_results = retrieve(
        query=darglobal_query,
        top_k=COMPARISON_TOP_K,
        source_filter="DarGlobal"
    )

    wasalt_results = retrieve(
        query=wasalt_query,
        top_k=COMPARISON_TOP_K,
        source_filter="Wasalt"
    )

    return darglobal_results + wasalt_results


def prepare_question(question, conversation_history=None):
    """
    Shared query resolution, retrieval and context preparation.
    Used by both normal and streaming responses.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    original_question = question.strip()

    history = get_recent_history(conversation_history)

    # Step 1: Resolve references from previous conversation.
    resolved_question = resolve_question(
        original_question,
        history
    )

    print(f"[CHAT] Original question: {original_question}")
    print(f"[CHAT] Resolved question: {resolved_question}")

    # Step 2: Route the resolved question.
    comparison_mode = is_comparison_query(resolved_question)
    selected_source = classify_source(resolved_question)

    # Step 3: Reject clearly unrelated questions.
    if is_out_of_domain_query(resolved_question):
        return {
            "answer": OUT_OF_DOMAIN_MESSAGE,
            "sources": [],
            "selected_source": selected_source,
            "query_type": "out_of_domain",
            "retrieved_count": 0,
            "relevant_count": 0,
            "resolved_question": resolved_question
        }, None

    # Step 4: Retrieve evidence.
    if comparison_mode:
        results = retrieve_comparison_results(resolved_question)
        distance_limit = COMPARISON_MAX_DISTANCE

    else:
        retrieval_query = expand_retrieval_query(
            resolved_question,
            source=selected_source
        )

        results = retrieve(
            query=retrieval_query,
            top_k=TOP_K,
            source_filter=selected_source
        )

        distance_limit = MAX_DISTANCE

    # Step 5: Filter weak semantic matches.
    relevant_results = [
        result
        for result in results
        if result["distance"] <= distance_limit
    ]

    # Step 6: Handle missing evidence.
    if not relevant_results:
        return {
            "answer": NO_INFORMATION_MESSAGE,
            "sources": [],
            "selected_source": selected_source,
            "query_type": (
                "comparison" if comparison_mode else "standard"
            ),
            "retrieved_count": len(results),
            "relevant_count": 0,
            "resolved_question": resolved_question
        }, None

    # Step 7: Organize comparison evidence.
    if comparison_mode:
        relevant_results.sort(
            key=lambda result: (
                result["metadata"].get("source", ""),
                result["distance"]
            )
        )

    # Step 8: Build context and collect sources.
    context_parts = []
    sources = {}

    for result in relevant_results:
        metadata = result["metadata"]

        source_name = metadata.get("source", "Unknown")
        title = metadata.get("title", "Untitled")
        url = metadata.get("url", "")

        context_parts.append(
            f"Source: {source_name}\n"
            f"Title: {title}\n"
            f"Content: {result['content']}"
        )

        if url and url not in sources:
            sources[url] = {
                "source": source_name,
                "title": title,
                "url": url
            }

    context = "\n\n".join(context_parts)

    metadata = {
        "sources": list(sources.values()),
        "selected_source": selected_source,
        "query_type": (
            "comparison" if comparison_mode else "standard"
        ),
        "retrieved_count": len(results),
        "relevant_count": len(relevant_results),
        "resolved_question": resolved_question
    }

    return metadata, context


def ask_question(question, conversation_history=None):
    metadata, context = prepare_question(
        question,
        conversation_history
    )

    if context is None:
        return metadata

    comparison_mode = metadata["query_type"] == "comparison"

    answer = generate_answer(
        question=question.strip(),
        context=context,
        comparison_mode=comparison_mode,
        conversation_history=get_recent_history(conversation_history)
    )

    return {
        **metadata,
        "answer": answer
    }


def ask_question_stream(question, conversation_history=None):
    metadata, context = prepare_question(
        question,
        conversation_history
    )

    if context is None:
        return {
            **metadata,
            "stream": iter([metadata["answer"]])
        }

    comparison_mode = metadata["query_type"] == "comparison"

    answer_stream = generate_answer_stream(
        question=question.strip(),
        context=context,
        comparison_mode=comparison_mode,
        conversation_history=get_recent_history(conversation_history)
    )

    return {
        **metadata,
        "stream": answer_stream
    }


if __name__ == "__main__":
    question = input("\nAsk DarGlobal & Wasalt AI: ")

    result = ask_question(question)

    print("\nAI ANSWER:")
    print(result["answer"])

    print("\nRESOLVED QUESTION:")
    print(result.get("resolved_question", question))

    print("\nRETRIEVAL INFORMATION:")
    print("Query type:", result["query_type"])
    print("Selected source:", result["selected_source"] or "Both")
    print("Retrieved chunks:", result["retrieved_count"])
    print("Relevant chunks:", result["relevant_count"])

    print("\nSOURCES:")

    if not result["sources"]:
        print("No relevant sources found.")

    for source in result["sources"]:
        print(f"{source['source']} - {source['title']}")
        print(source["url"])
