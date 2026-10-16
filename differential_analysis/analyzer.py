
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR / "results" / "behavior_observations.json"
)

OUTPUT_PATH = (
    BASE_DIR / "results" / "drift_report.json"
)


FIELD_CATEGORIES = {
    "output": [
        "currency",
        "subtotal",
        "discount",
        "tax",
        "final_total",
    ],
    "state": [
        "order_created",
    ],
    "error": [
        "status",
        "error_type",
        "error_message",
    ],
    "workflow": [
        "business_decision",
    ],
}


def compare_observation(observation):
    """
    Compare normalized legacy and modernized
    behavior for one test case.
    """

    legacy = observation["legacy"]
    modernized = observation["modernized"]

    differences = []
    category_flags = {
        category: False
        for category in FIELD_CATEGORIES
    }

    for category, fields in FIELD_CATEGORIES.items():

        for field in fields:

            legacy_value = legacy.get(field)
            modernized_value = modernized.get(field)

            if legacy_value != modernized_value:

                differences.append({
                    "category": category,
                    "field": field,
                    "legacy_value": legacy_value,
                    "modernized_value": modernized_value,
                })

                category_flags[category] = True

    return {
        "test_id": observation["test_id"],
        "description": observation["description"],
        "has_drift": len(differences) > 0,
        "difference_count": len(differences),
        "category_flags": category_flags,
        "differences": differences,
        "legacy": legacy,
        "modernized": modernized,
    }


def analyze_observations(observations):
    """
    Analyze an in-memory collection of
    recorded observations.
    """

    comparisons = [
        compare_observation(observation)
        for observation in observations
    ]

    drifted_cases = [
        result["test_id"]
        for result in comparisons
        if result["has_drift"]
    ]

    return {
        "total_test_cases": len(comparisons),
        "drifted_test_cases": len(drifted_cases),
        "drifted_case_ids": drifted_cases,
        "comparisons": comparisons,
    }


def run_differential_analysis():
    """
    Load recorded observations, compare
    behaviors, and save the drift report.
    """

    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        observations = json.load(file)

    report = analyze_observations(observations)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nDIFFERENTIAL ANALYSIS REPORT")
    print("=" * 55)

    print(
        f"Total test cases: "
        f"{report['total_test_cases']}"
    )

    print(
        f"Cases with drift: "
        f"{report['drifted_test_cases']}"
    )

    print(
        f"Drifted IDs: "
        f"{report['drifted_case_ids']}"
    )

    for comparison in report["comparisons"]:

        if not comparison["has_drift"]:
            continue

        print(
            f"\n{comparison['test_id']}: "
            f"{comparison['description']}"
        )

        for difference in comparison["differences"]:

            print(
                f"  {difference['field']}: "
                f"{difference['legacy_value']} -> "
                f"{difference['modernized_value']}"
            )

    print(f"\nReport saved to: {OUTPUT_PATH}")

    return report


if __name__ == "__main__":
    run_differential_analysis()
