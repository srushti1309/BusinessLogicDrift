
from decimal import Decimal, InvalidOperation

from config import (
    DISCOUNT_THRESHOLD,
    DISCOUNT_RATE,
    TAX_RATE,
    CURRENCY,
    CURRENCY_QUANTUM,
    ROUNDING_MODE,
)


def round_money(value):
    """
    Round a Decimal amount to two decimal places.
    """
    return value.quantize(
        CURRENCY_QUANTUM,
        rounding=ROUNDING_MODE
    )


def validation_error(message):
    """
    Return a standardized failed checkout response.
    """
    return {
        "status": "error",
        "error_type": "VALIDATION_ERROR",
        "error_message": message,
        "business_decision": "REJECTED",
        "order_created": False,
        "currency": CURRENCY,
        "subtotal": None,
        "discount": None,
        "tax": None,
        "final_total": None,
    }


def process_checkout(request):
    """
    Process a checkout request using the legacy
    business rules.

    Input:
        {
            "quantity": 2,
            "unit_price": "500.00"
        }

    Returns a structured checkout response.
    """

    # STEP 1: Extract the input values.
    quantity = request.get("quantity")
    unit_price_raw = request.get("unit_price")

    # STEP 2: Validate quantity.
    # bool must be rejected because bool is a subclass of int.
    if type(quantity) is not int or quantity <= 0:
        return validation_error(
            "Quantity must be a positive integer."
        )

    # STEP 3: Validate and convert unit price.
    try:
        if (
            isinstance(unit_price_raw, bool)
            or unit_price_raw is None
        ):
            raise ValueError("Invalid price")

        unit_price = Decimal(str(unit_price_raw))

    except (InvalidOperation, ValueError, TypeError):
        return validation_error(
            "Unit price must be a valid non-negative number."
        )

    if not unit_price.is_finite() or unit_price < 0:
        return validation_error(
            "Unit price must be a valid non-negative number."
        )

    # STEP 4: Calculate subtotal.
    subtotal = round_money(
        Decimal(quantity) * unit_price
    )

    # STEP 5: Apply the discount.
    if subtotal >= DISCOUNT_THRESHOLD:
        discount = round_money(
            subtotal * DISCOUNT_RATE
        )
    else:
        discount = Decimal("0.00")

    # STEP 6: Calculate taxable amount.
    taxable_amount = round_money(
        subtotal - discount
    )

    # STEP 7: Calculate tax.
    tax = round_money(
        taxable_amount * TAX_RATE
    )

    # STEP 8: Calculate final total.
    final_total = round_money(
        taxable_amount + tax
    )

    # STEP 9: Return structured business behavior.
    return {
        "status": "success",
        "error_type": None,
        "error_message": None,
        "business_decision": "APPROVED",
        "order_created": True,
        "currency": CURRENCY,
        "subtotal": str(subtotal),
        "discount": str(discount),
        "tax": str(tax),
        "final_total": str(final_total),
    }
