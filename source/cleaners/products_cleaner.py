import pandas as pd
from .base_cleaner import BaseCleaner
from models.product_model import Product

class ProductsCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.remove_duplicates(data)
        data = self.handle_nulls(data, strategy='drop')

        for _, row in data.iterrows():
            try:
                product = Product(**row.to_dict())
                self.valid_records.append(product.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": row.to_dict(), "error": str(e)})

        return pd.DataFrame(self.valid_records)