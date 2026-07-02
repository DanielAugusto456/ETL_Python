from pydantic import BaseModel, Field, field_validator
from validations import validation as va

class Product(BaseModel):

    name: str = Field(..., description="The name of the product", max_length=50)

    categoryID: int = Field(..., description="The ID of the category the product belongs to")

    price: float = Field(..., description="The price of the product")

    stock: int = Field(..., description="The available stock of the product")

    @field_validator("name")
    @classmethod
    def validate_string_fields(cls, value: str) -> str:
        return va.validate_string_fields(value)