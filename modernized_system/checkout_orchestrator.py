
from config import CURRENCY

from modernized_system.validation_service import (
    validate_checkout_request,
)
from modernized_system.pricing_service import (
    calculate_subtotal,
    round_money,
)
from modernized_system.discount_service import (
    calculate_discount,
)
from modernized_system.tax_service import (
    calculate_tax,
)


def validation_error(message):
    """
    Construct a standardized validation error.
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
    Process a checkout request by coordinating
    the modernized business-logic modules.
    """

    # STEP 1: Validate the request.
    is_valid, validated_data, error_message = (
        validate_checkout_request(request)
    )

    if not is_valid:
        return validation_error(error_message)

    # STEP 2: Extract validated values.
    quantity = validated_data["quantity"]
    unit_price = validated_data["unit_price"]

    # STEP 3: Calculate subtotal.
    subtotal = calculate_subtotal(
        quantity,
        unit_price
    )

    # STEP 4: Calculate discount.
    discount = calculate_discount(subtotal)

    # STEP 5: Calculate taxable amount.
    taxable_amount = round_money(
        subtotal - discount
    )

    # STEP 6: Calculate tax.
    tax = calculate_tax(taxable_amount)

    # STEP 7: Calculate final total.
    final_total = round_money(
        taxable_amount + tax
    )

    # STEP 8: Construct the response.
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
