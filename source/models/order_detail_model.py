from pydantic import BaseModel, Field, field_validator

class OrderDetail(BaseModel):
    order_id: int = Field(..., description="The ID of the order")

    product_id: int = Field(..., description="The ID of the product")

    quantity: int = Field(..., description="The quantity of the product in the order")

    totalPrice: float = Field(..., description="The price of the product in the order")