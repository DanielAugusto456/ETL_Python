from pydantic import BaseModel, Field, field_validator
from validations import validation as va

class OrderDetail(BaseModel):
    order_id: int = Field(..., description="The ID of the order")

    product_id: int = Field(..., description="The ID of the product")

    quantity: int = Field(..., description="The quantity of the product in the order")

    total_price: float = Field(..., description="The price of the product in the order")

    @field_validator('total_price')
    @classmethod
    def validate_total_price(cls, value):
        if value < 0:
            raise ValueError('Total price must be greater than or equal to 0')
        return round(value, 2)
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, value):
        if value <= 0:
            raise ValueError('Quantity must be greater than 0')
        return value