
import json
from pathlib import Path

from legacy_system.checkout import process_checkout


BASE_DIR = Path(__file__).resolve().parent.parent

TEST_CASES_PATH = (
    BASE_DIR / "test_cases" / "checkout_cases.json"
)

RESULTS_PATH = (
    BASE_DIR / "results" / "legacy_results.json"
)


def run_legacy_tests():
    """
    Execute all predefined test cases against
    the legacy checkout implementation.
    """

    with open(
        TEST_CASES_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        test_cases = json.load(file)

    results = []

    print("\n" + "=" * 65)
    print("LEGACY CHECKOUT SYSTEM - TEST EXECUTION")
    print("=" * 65)

    for test_case in test_cases:

        request = {
            "quantity": test_case["quantity"],
            "unit_price": test_case["unit_price"]
        }

        response = process_checkout(request)

        result = {
            "test_id": test_case["test_id"],
            "description": test_case["description"],
            "request": request,
            "response": response
        }

        results.append(result)

        print(f"\nTest: {test_case['test_id']}")
        print(f"Description: {test_case['description']}")
        print(f"Status: {response['status']}")
        print(
            f"Business Decision: "
            f"{response['business_decision']}"
        )

        if response["status"] == "success":
            print(f"Subtotal: {response['subtotal']}")
            print(f"Discount: {response['discount']}")
            print(f"Tax: {response['tax']}")
            print(f"Final Total: {response['final_total']}")
        else:
            print(
                f"Error: {response['error_message']}"
            )

        print("-" * 65)

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"\nExecuted {len(results)} legacy test cases."
    )
    print(f"Results saved to: {RESULTS_PATH}")

    return results


if __name__ == "__main__":
    run_legacy_tests()
