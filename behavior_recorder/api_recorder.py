
import json
import os
from pathlib import Path

import httpx

from behavior_recorder.normalizer import (
    normalize_response,
)


BASE_DIR = Path(__file__).resolve().parent.parent

TEST_CASES_PATH = (
    BASE_DIR / "test_cases" / "checkout_cases.json"
)

OUTPUT_PATH = (
    BASE_DIR / "results" / "api_behavior_observations.json"
)

LEGACY_URL = os.getenv(
    "LEGACY_URL",
    "http://127.0.0.1:8001",
)

MODERNIZED_URL = os.getenv(
    "MODERNIZED_URL",
    "http://127.0.0.1:8002",
)


def record_api_behaviors():
    """
    Execute identical requests against the
    legacy and modernized HTTP applications.
    """

    with open(
        TEST_CASES_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        test_cases = json.load(file)

    observations = []

    with httpx.Client(timeout=15.0) as client:

        for test_case in test_cases:

            request = {
                "quantity": test_case["quantity"],
                "unit_price": test_case["unit_price"],
            }

            legacy_response = client.post(
                f"{LEGACY_URL}/checkout",
                json=request,
            )

            modernized_response = client.post(
                f"{MODERNIZED_URL}/checkout",
                json=request,
            )

            # Fail explicitly on transport/API errors.
            # We must not confuse infrastructure failures
            # with valid business-logic drift.
            legacy_response.raise_for_status()
            modernized_response.raise_for_status()

            observation = {
                "test_id": test_case["test_id"],
                "description": test_case["description"],
                "request": request,
                "legacy": normalize_response(
                    legacy_response.json()
                ),
                "modernized": normalize_response(
                    modernized_response.json()
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
        f"Recorded API behavior for "
        f"{len(observations)} test cases."
    )

    return observations


if __name__ == "__main__":
    record_api_behaviors()
