import pandas as pd

class normalizer:

    @staticmethod
    def phone_normalizer(phone: str) -> str:
        normalized_phone = ''.join(filter(str.isdigit, phone))
        return normalized_phone
    
    @staticmethod
    def email_normalizer(email: str) -> str:
        normalized_email = email.strip().lower()
        return normalized_email
    
    @staticmethod
    def name_normalizer(name: str) -> str:
        normalized_name = name.strip().title()
        return normalized_name