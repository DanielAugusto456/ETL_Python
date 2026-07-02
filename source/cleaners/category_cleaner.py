import pandas as pd
from .base_cleaner import BaseCleaner
from models.category_model import Category
from normalizer import normalizer
from config.database import get_creds

class CategoryCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data["Category"].copy()

        data = self.remove_duplicates(data)
        data = self.handle_nulls(data, strategy='drop')

        creds = get_creds()

        categories_in_db = pd.read_sql_query("SELECT CategoryName FROM Category", con=creds.engine)

        categories_db = set(categories_in_db['CategoryName'])

        data = data[~data.isin(categories_db)]

        if data.empty:
            print("No new categories to insert.")
            return pd.DataFrame()

        for _, row in data.iterrows():
            try:
                category = Category(**row.to_dict())
                self.valid_records.append(category.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": row.to_dict(), "error": str(e)})

        return pd.DataFrame(self.valid_records)