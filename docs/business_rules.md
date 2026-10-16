
# Checkout Business Rules — Version 1

## Purpose

This document defines the expected checkout behavior used to evaluate the legacy and modernized implementations.

The legacy implementation is a reference system, but the written rules are the authority for expected behavior.

## Rule BR-01: Subtotal

subtotal = quantity * unit_price

## Rule BR-02: Discount

If subtotal >= 1000.00, apply a 10% discount.

Otherwise, discount = 0.00.

## Rule BR-03: Tax

Apply 18% tax after the discount.

taxable_amount = subtotal - discount

tax = taxable_amount * 0.18

## Rule BR-04: Final Total

final_total = subtotal - discount + tax

## Rule BR-05: Validation

- quantity must be a positive integer.
- unit_price must be greater than or equal to zero.
- Invalid requests must produce a structured validation error.

## Rule BR-06: Currency

- Currency is INR.
- Use Python Decimal for monetary calculations.
- Monetary amounts are rounded to two decimal places using ROUND_HALF_UP.
- Round subtotal, discount, taxable amount, tax, and final total at their respective calculation stages.

## Rule BR-07: State

- Valid checkout requests produce a successful order decision.
- Invalid checkout requests must not create an order.
- For Version 1, no persistent database state is required.

## Rule BR-08: Comparison

Both systems receive identical requests.

Comparison must consider:
- Business outputs
- Validation errors
- Business decisions
- Relevant state observations

Differences must be recorded without automatically assuming the legacy implementation is correct.
