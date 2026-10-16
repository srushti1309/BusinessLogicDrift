
import json
from pathlib import Path

from legacy_system.checkout import (
    process_checkout as legacy_checkout,
)

from modernized_system.checkout_orchestrator import (
    process_checkout as modernized_checkout,
)

from behavior_recorder.normalizer import (
    normalize_response,
)


BASE_DIR = Path(__file__).resolve().parent.parent

TEST_CASES_PATH = (
    BASE_DIR / "test_cases" / "checkout_cases.json"
)

OUTPUT_PATH = (
    BASE_DIR / "results" / "behavior_observations.json"
)


def record_behaviors():
    """
    Execute identical requests against both
    implementations and record their behavior.
    """

    with open(
        TEST_CASES_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        test_cases = json.load(file)

    observations = []

    for test_case in test_cases:

        request = {
            "quantity": test_case["quantity"],
            "unit_price": test_case["unit_price"],
        }

        legacy_response = legacy_checkout(
            request.copy()
        )

        modernized_response = modernized_checkout(
            request.copy()
        )

        observation = {
            "test_id": test_case["test_id"],
            "description": test_case["description"],
            "request": request,
            "legacy": normalize_response(
                legacy_response
            ),
            "modernized": normalize_response(
                modernized_response
            ),
        }

        observations.append(observation)

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
            observations,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Recorded behavior for "
        f"{len(observations)} test cases."
    )

    print(f"Saved to: {OUTPUT_PATH}")

    return observations


if __name__ == "__main__":
    record_behaviors()
