
from decimal import Decimal, ROUND_HALF_UP

# Checkout business configuration
DISCOUNT_THRESHOLD = Decimal("1000.00")
DISCOUNT_RATE = Decimal("0.10")
TAX_RATE = Decimal("0.18")

CURRENCY = "INR"
CURRENCY_QUANTUM = Decimal("0.01")
ROUNDING_MODE = ROUND_HALF_UP

# Logic Drift Index configuration
# These weights will be used in a later milestone.
LDI_WEIGHTS = {
    "output": 0.40,
    "state": 0.25,
    "error": 0.20,
    "workflow": 0.15
}

LDI_THRESHOLD = 5.0

# Project paths
TEST_CASE_FILE = "test_cases/checkout_cases.json"
RESULTS_DIRECTORY = "results"
