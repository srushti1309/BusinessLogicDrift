
import json
from pathlib import Path

from config import (
    DISCOUNT_THRESHOLD,
    DISCOUNT_RATE,
    TAX_RATE,
    LDI_WEIGHTS,
)

BASE_DIR = Path(__file__).resolve().parent

required_folders = [
    "legacy_system",
    "modernized_system",
    "test_cases",
    "behavior_recorder",
    "differential_analysis",
    "ldi_calculator",
    "results",
    "tests",
    "docs",
]

required_files = [
    ".gitignore",
    "config.py",
    "docs/business_rules.md",
    "test_cases/checkout_cases.json",
]

print("\nChecking project structure...")

for folder in required_folders:
    path = BASE_DIR / folder
    assert path.is_dir(), f"Missing folder: {folder}"
    print(f"[OK] {folder}")

for filename in required_files:
    path = BASE_DIR / filename
    assert path.is_file(), f"Missing file: {filename}"
    print(f"[OK] {filename}")

print("\nChecking test cases...")

with open(
    BASE_DIR / "test_cases/checkout_cases.json",
    "r",
    encoding="utf-8",
) as file:
    test_cases = json.load(file)

assert len(test_cases) == 8, "Expected 8 test cases"

ids = [case["test_id"] for case in test_cases]
assert len(ids) == len(set(ids)), "Duplicate test IDs found"

for case in test_cases:
    assert all(
        key in case
        for key in ("test_id", "description", "quantity", "unit_price")
    ), f"Incomplete test case: {case}"

print(f"[OK] Loaded {len(test_cases)} unique test cases")

print("\nChecking configuration...")

assert DISCOUNT_THRESHOLD > 0
assert 0 <= DISCOUNT_RATE <= 1
assert 0 <= TAX_RATE <= 1
assert abs(sum(LDI_WEIGHTS.values()) - 1.0) < 1e-9

print("[OK] Business constants valid")
print("[OK] LDI weights sum to 1.0")

print("\nMILESTONE 2 COMPLETED SUCCESSFULLY")
