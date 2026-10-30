
import ast
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

SOURCE_PATH = (
    BASE_DIR / "modernized_system" / "discount_service.py"
)

CANDIDATE_PATH = (
    BASE_DIR / "repair_engine" / "candidate_discount_service.py"
)

PATCH_REPORT_PATH = (
    BASE_DIR / "results" / "patch_report.json"
)


FAULTY_EXPRESSION = (
    "subtotal > DISCOUNT_THRESHOLD"
)

CORRECTED_EXPRESSION = (
    "subtotal >= DISCOUNT_THRESHOLD"
)


def generate_candidate_patch():

    source = SOURCE_PATH.read_text(
        encoding="utf-8"
    )

    occurrences = source.count(FAULTY_EXPRESSION)

    if occurrences != 1:
        raise ValueError(
            "Expected exactly one known faulty "
            f"expression, found {occurrences}."
        )

    candidate = source.replace(
        FAULTY_EXPRESSION,
        CORRECTED_EXPRESSION,
        1
    )

    # Reject syntactically invalid candidates.
    ast.parse(candidate)

    CANDIDATE_PATH.write_text(
        candidate,
        encoding="utf-8"
    )

    report = {
        "repair_strategy": "deterministic_pattern_replacement",
        "source_file": str(SOURCE_PATH),
        "candidate_file": str(CANDIDATE_PATH),
        "original_expression": FAULTY_EXPRESSION,
        "repaired_expression": CORRECTED_EXPRESSION,
        "syntax_valid": True,
        "original_modified": False,
        "status": "candidate_generated",
    }

    PATCH_REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    PATCH_REPORT_PATH.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    print("\nCANDIDATE REPAIR GENERATED")
    print("=" * 55)
    print("Original:", FAULTY_EXPRESSION)
    print("Candidate:", CORRECTED_EXPRESSION)
    print("Syntax valid: True")
    print("Original source left unchanged.")
    print(f"Candidate saved: {CANDIDATE_PATH}")

    return report


if __name__ == "__main__":
    generate_candidate_patch()
