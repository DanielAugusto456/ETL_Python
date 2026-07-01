import pandas as pd
from .base_cleaner import BaseCleaner
from models.product_model import Product
from normalizer import normalizer

class CustomersCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.remove_duplicates(data)
        data = self.handle_nulls(data, strategy='drop')

        for _, row in data.iterrows():
            try:
                row['phone'] = normalizer.phone_normalizer(row['phone'])
                row['email'] = normalizer.email_normalizer(row['email'])
                row['name'] = normalizer.name_normalizer(row['name'])
                product = Product(**row.to_dict())
                self.valid_records.append(product.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": row.to_dict(), "error": str(e)})

        return pd.DataFrame(self.valid_records)