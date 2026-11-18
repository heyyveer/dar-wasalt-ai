
import json
import re
import time
from datetime import datetime
from pathlib import Path

from rag.chat import ask_question


TEST_CASES = [
    {
        "id": "Q1",
        "category": "Wasalt overview",
        "question": "What is Wasalt and what services does it offer?",
        "expected_terms": ["wasalt"],
        "manual_review": True,
    },
    {
        "id": "Q2",
        "category": "DarGlobal portfolio",
        "question": "What is DarGlobal's development portfolio?",
        "expected_terms": ["23"],
        "manual_review": True,
    },
    {
        "id": "Q3",
        "category": "Specific fact",
        "question": "What is the Rayana infrastructure contract value?",
        "expected_terms": ["338", "sar"],
        "manual_review": True,
    },
    {
        "id": "Q4",
        "category": "Wasalt auctions",
        "question": "Does Wasalt organize real estate auctions?",
        "expected_terms": ["auction"],
        "manual_review": True,
    },
    {
        "id": "Q5",
        "category": "Missing information",
        "question": "What is the price of a property in Riyadh?",
        "expected_any": [
            "not available",
            "couldn't find",
            "insufficient information",
            "not found",
            "no specific price",
            "does not contain",
            "no specific pricing information",
            "does not provide",
            "doesn't provide",
            "without giving any price",
        ],
        "manual_review": True,
    },
    {
        "id": "Q6",
        "category": "Out-of-domain question",
        "question": "What is the weather in Dubai?",
        "expected_any": [
            "not available",
            "couldn't find",
            "knowledge base",
            "weather data",
            "insufficient information",
            "does not contain",
            "no weather",
            "outside the scope",
        ],
        "manual_review": True,
    },
    {
        "id": "Q7",
        "category": "Company comparison",
        "question": "Compare DarGlobal and Wasalt.",
        "expected_terms": ["darglobal", "wasalt"],
        "manual_review": True,
    },
]


def evaluate_answer(answer, test_case):
    normalized = answer.lower()

    expected_terms = test_case.get("expected_terms", [])
    expected_any = test_case.get("expected_any", [])

    matched_terms = [
        term for term in expected_terms
        if term.lower() in normalized
    ]

    matched_any = [
        term for term in expected_any
        if term.lower() in normalized
    ]

    all_expected_found = (
        len(matched_terms) == len(expected_terms)
    )

    any_expected_found = (
        not expected_any or len(matched_any) > 0
    )

    passed = all_expected_found and any_expected_found

    return {
        "passed": passed,
        "matched_expected_terms": matched_terms,
        "missing_expected_terms": [
            term for term in expected_terms
            if term.lower() not in normalized
        ],
        "matched_expected_phrases": matched_any,
        "manual_review_required": test_case.get(
            "manual_review", True
        ),
    }


def run_evaluation():
    report = {
        "project": "DarGlobal-Wasalt AI",
        "generated_at": datetime.now().astimezone().isoformat(),
        "total_questions": len(TEST_CASES),
        "results": [],
    }

    for index, test_case in enumerate(TEST_CASES, start=1):
        print("\n" + "=" * 85)
        print(
            f"{index}/{len(TEST_CASES)} | "
            f"{test_case['id']} | {test_case['category']}"
        )
        print("=" * 85)

        print("QUESTION:", test_case["question"])

        start = time.perf_counter()

        try:
            result = ask_question(test_case["question"])

            elapsed = time.perf_counter() - start
            answer = result["answer"]

            checks = evaluate_answer(answer, test_case)

            evaluation_result = {
                "id": test_case["id"],
                "category": test_case["category"],
                "question": test_case["question"],
                "answer": answer,
                "latency_seconds": round(elapsed, 2),
                "retrieved_count": result["retrieved_count"],
                "relevant_count": result["relevant_count"],
                "selected_source": result["selected_source"],
                "query_type": result["query_type"],
                "sources": result["sources"],
                "checks": checks,
                "status": "PASSED" if checks["passed"] else "REVIEW",
                "error": None,
            }

            print("\nANSWER:")
            print(answer)

            print("\nRETRIEVAL:")
            print("Retrieved:", result["retrieved_count"])
            print("Relevant:", result["relevant_count"])

            print("\nEVALUATION:")
            print("Status:", evaluation_result["status"])
            print("Latency:", round(elapsed, 2), "seconds")

        except Exception as error:
            elapsed = time.perf_counter() - start

            evaluation_result = {
                "id": test_case["id"],
                "category": test_case["category"],
                "question": test_case["question"],
                "latency_seconds": round(elapsed, 2),
                "status": "ERROR",
                "error": f"{type(error).__name__}: {error}",
            }

            print("\nERROR:", evaluation_result["error"])

        report["results"].append(evaluation_result)

    successful = [
        item for item in report["results"]
        if item["status"] != "ERROR"
    ]

    passed = [
        item for item in report["results"]
        if item["status"] == "PASSED"
    ]

    latencies = [
        item["latency_seconds"]
        for item in successful
    ]

    report["summary"] = {
        "total": len(report["results"]),
        "successful": len(successful),
        "errors": len(report["results"]) - len(successful),
        "passed_keyword_checks": len(passed),
        "review_required": len(successful),
        "average_latency_seconds": (
            round(sum(latencies) / len(latencies), 2)
            if latencies else 0
        ),
    }

    output_dir = Path("evaluation_reports")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"rag_evaluation_{timestamp}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print("\n" + "=" * 85)
    print("EVALUATION SUMMARY")
    print("=" * 85)

    for key, value in report["summary"].items():
        print(f"{key}: {value}")

    print("\nReport saved to:", output_file)


if __name__ == "__main__":
    run_evaluation()
