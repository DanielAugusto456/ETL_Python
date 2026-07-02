import pandas as pd
from .base_cleaner import BaseCleaner
from models.customer_model import Customer
from normalizer import normalizer

class CustomersCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.remove_duplicates(data)
        data = self.handle_nulls(data, strategy='drop')

        for _, row in data.iterrows():
            try:
                row['Phone'] = normalizer.phone_normalizer(row['Phone'])
                row['Email'] = normalizer.email_normalizer(row['Email'])
                row['FirstName'] = normalizer.name_normalizer(row['FirstName'])
                row['LastName'] = normalizer.name_normalizer(row['LastName'])
                customer = Customer(**row.to_dict())
                self.valid_records.append(customer.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": row.to_dict(), "error": str(e)})

        return pd.DataFrame(self.valid_records)