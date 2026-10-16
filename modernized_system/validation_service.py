
from decimal import Decimal, InvalidOperation


def validate_checkout_request(request):
    """
    Validate checkout input.

    Returns:
        (True, validated_data, None) for valid input.
        (False, None, error_message) for invalid input.
    """

    quantity = request.get("quantity")
    unit_price_raw = request.get("unit_price")

    if type(quantity) is not int or quantity <= 0:
        return (
            False,
            None,
            "Quantity must be a positive integer."
        )

    try:
        if (
            isinstance(unit_price_raw, bool)
            or unit_price_raw is None
        ):
            raise ValueError("Invalid price")

        unit_price = Decimal(str(unit_price_raw))

    except (InvalidOperation, ValueError, TypeError):
        return (
            False,
            None,
            "Unit price must be a valid non-negative number."
        )

    if not unit_price.is_finite() or unit_price < 0:
        return (
            False,
            None,
            "Unit price must be a valid non-negative number."
        )

    return (
        True,
        {
            "quantity": quantity,
            "unit_price": unit_price,
        },
        None
    )
