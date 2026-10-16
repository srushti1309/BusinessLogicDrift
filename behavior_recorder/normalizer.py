
from decimal import Decimal, InvalidOperation


MONETARY_FIELDS = {
    "subtotal",
    "discount",
    "tax",
    "final_total",
}

OBSERVED_FIELDS = [
    "status",
    "error_type",
    "error_message",
    "business_decision",
    "order_created",
    "currency",
    "subtotal",
    "discount",
    "tax",
    "final_total",
]


def normalize_money(value):
    """
    Convert monetary values into a canonical
    two-decimal-place string.

    This prevents differences such as:
        "100.0" vs "100.00"

    from being incorrectly classified as drift.
    """

    if value is None:
        return None

    try:
        amount = Decimal(str(value))

        if not amount.is_finite():
            return str(value)

        return format(amount, ".2f")

    except (InvalidOperation, ValueError, TypeError):
        return str(value)


def normalize_response(response):
    """
    Extract relevant business behavior and
    normalize monetary representations.

    Missing fields are represented as None
    in this initial prototype.
    """

    normalized = {}

    for field in OBSERVED_FIELDS:

        value = response.get(field)

        if field in MONETARY_FIELDS:
            normalized[field] = normalize_money(value)
        else:
            normalized[field] = value

    return normalized
