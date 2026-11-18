
import re


def classify_source(query):
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    normalized_query = query.lower().strip()

    darglobal_keywords = [
        "darglobal",
        "dar global",
        "rayana",
        "amaya",
        "mad muscat",
        "muscat marine",
        "aida",
        "azure oceanfront",
        "fendi casa",
        "wadi safar"
    ]

    wasalt_keywords = [
        "wasalt",
        "property listing",
        "property listings",
        "properties for sale",
        "properties for rent",
        "property price",
        "property prices",
        "real estate services",
        "property search",
        "auction",
        "auctions"
    ]

    mentions_darglobal = any(
        keyword in normalized_query
        for keyword in darglobal_keywords
    )

    mentions_wasalt = any(
        keyword in normalized_query
        for keyword in wasalt_keywords
    )

    if mentions_darglobal and mentions_wasalt:
        return None

    if mentions_darglobal:
        return "DarGlobal"

    if mentions_wasalt:
        return "Wasalt"

    property_keywords = [
        "property",
        "properties",
        "apartment",
        "villa",
        "real estate",
        "house",
        "flat",
        "listing",
        "rent",
        "buy",
        "purchase"
    ]

    mentions_property = any(
        keyword in normalized_query
        for keyword in property_keywords
    )

    mentions_riyadh = "riyadh" in normalized_query

    if mentions_property and mentions_riyadh:
        return "Wasalt"

    return None


def expand_retrieval_query(query, source=None):
    """
    Add domain-specific terms to improve semantic retrieval.
    The original user question remains unchanged for answer generation.
    """

    normalized_query = query.lower()

    entity_expansions = {
        "rayana": (
            "Rayana community Wadi Safar Riyadh DarGlobal "
            "ultra-exclusive community infrastructure project"
        ),
        "amaya": (
            "Amaya flagship masterplan Jeddah Saudi Arabia "
            "DarGlobal development contractor"
        ),
        "mad muscat": (
            "MAD Muscat Marine Art and Digital District "
            "Muscat Oman DarGlobal development"
        ),
        "muscat marine": (
            "MAD Muscat Marine Art and Digital District "
            "Muscat Oman DarGlobal development"
        ),
        "aida": (
            "AIDA clifftop community Muscat Oman "
            "DarGlobal luxury real estate development"
        ),
        "azure oceanfront": (
            "Azure Oceanfront Villas FENDI Casa AIDA "
            "Muscat Oman DarGlobal luxury villas"
        ),
        "fendi casa": (
            "FENDI Casa luxury interiors Azure Oceanfront Villas "
            "DarGlobal AIDA Oman"
        )
    }

    expansions = []

    for entity, expansion in entity_expansions.items():
        if entity in normalized_query:
            expansions.append(expansion)

    if source == "Wasalt":
        if "auction" in normalized_query:
            expansions.append(
                "Wasalt Saudi Arabia real estate auctions "
                "auction services property auction platform"
            )
        elif not expansions:
            expansions.append(
                "Wasalt Saudi Arabia PropTech real estate platform "
                "property search verified listings services"
            )

    elif source == "DarGlobal" and not expansions:
        expansions.append(
            "DarGlobal London-listed luxury real estate developer "
            "international projects development portfolio"
        )

    if not expansions:
        return query

    return query + " " + " ".join(expansions)


def is_out_of_domain_query(query):
    """
    Lightweight deterministic filter for clearly unrelated topics.

    This is not a general-purpose intent classifier. It only blocks
    explicit out-of-domain topics that this real-estate assistant
    is not designed to answer.
    """

    normalized_query = query.lower()

    out_of_domain_patterns = [
        r"\bweather\b",
        r"\bweather forecast\b",
        r"\btemperature\b",
        r"\brainfall\b",
        r"\brain\b",
        r"\bhumidity\b",
        r"\bwind speed\b",
        r"\bfifa\b",
        r"\bworld cup\b",
        r"\bfootball\b",
        r"\bsoccer\b",
        r"\bcricket\b",
        r"\bbasketball\b",
        r"\btennis\b",
        r"\bolympics\b",
        r"\bmatch score\b",
        r"\bsports news\b"
    ]

    return any(
        re.search(pattern, normalized_query)
        for pattern in out_of_domain_patterns
    )


if __name__ == "__main__":
    test_queries = [
        "Tell me about the Rayana project.",
        "What is DarGlobal?",
        "Explain Amaya project.",
        "What services does Wasalt offer?",
        "What is the exact price of a property in Riyadh?",
        "Who won FIFA World Cup 2022?",
        "What is the weather in Dubai?",
        "Compare DarGlobal and Wasalt."
    ]

    print("\nQUERY ROUTER VALIDATION")
    print("=" * 65)

    for query in test_queries:
        source = classify_source(query)
        expanded = expand_retrieval_query(query, source)
        out_of_domain = is_out_of_domain_query(query)

        print(f"\nQuery: {query}")
        print(f"Selected source: {source or 'Both sources'}")
        print(f"Out of domain: {out_of_domain}")
        print(f"Expanded query: {expanded}")
