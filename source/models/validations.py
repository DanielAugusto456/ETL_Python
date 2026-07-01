from pydantic import BaseModel, Field
class validation(BaseModel):

    @classmethod
    def validate_string_fields(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return value
    
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value:
            raise ValueError("Invalid email address")
        return value
    
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value.isdigit() or len(value) < 12:
            raise ValueError("Invalid phone number")
        return value