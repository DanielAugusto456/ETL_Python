import pandas as pd

class normalizer:

    @staticmethod
    def phone_normalizer(phone: str) -> str:
        # Remove all non-numeric characters
        normalized_phone = ''.join(filter(str.isdigit, phone))
        return normalized_phone
    
    @staticmethod
    def email_normalizer(email: str) -> str:
        # Convert to lowercase and strip whitespace
        normalized_email = email.strip().lower()
        return normalized_email
    
    @staticmethod
    def name_normalizer(name: str) -> str:
        # Convert to title case and strip whitespace
        normalized_name = name.strip().title()
        return normalized_name