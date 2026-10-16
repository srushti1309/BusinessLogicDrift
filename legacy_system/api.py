
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict
from typing import Any

from legacy_system.checkout import process_checkout


app = FastAPI(
    title="Legacy Checkout Monolith",
    version="1.0.0",
)


class CheckoutRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    quantity: Any
    unit_price: Any


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "system": "legacy_monolith",
    }


@app.post("/checkout")
def checkout(request: CheckoutRequest):
    return process_checkout(
        request.model_dump()
    )
