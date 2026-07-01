from pydantic import BaseModel, Field, field_validator
from validations import validation as va

class Customer(BaseModel):
    first_name: str = Field(..., description="The first name of the customer", max_length=50)

    last_name: str = Field(..., description="The last name of the customer", max_length=50)

    email: str = Field(..., description="The email address of the customer", max_length=100)

    phone: str = Field(..., description="The phone number of the customer", max_length=18)

    city: str = Field(..., description="The city of the customer", max_length=50)

    country: str = Field(..., description="The country of the customer", max_length=50)

    @field_validator("first_name", "last_name", "email", "city", "country")
    @classmethod
    def validate_string_fields(cls, value: str) -> str:
        return va.validate_string_fields(value)

    @field_validator("email")
    @classmethod
    def validate_string_fields(cls, value: str) -> str:
        return va.validate_email(value)
    
    