import pandas as pd
from .base_cleaner import BaseCleaner
from models.category_model import Category
from config.database import get_creds

class CategoryCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        categories = data["Category"].astype(str).str.strip()
        categories = self.remove_duplicates(categories)
        categories = self.handle_nulls(categories, strategy='drop')
        categories = categories[categories != ""]

        creds = get_creds()
        categories_in_db = pd.read_sql_query(
            "SELECT CategoryName FROM Category", con=creds.engine
        )
        categories_db = set(categories_in_db['CategoryName'])

        new_categories = self.filter_existing_in_db(categories, categories_db)

        if new_categories.empty:
            print("No new categories to insert.")
            return pd.DataFrame()

        for name in new_categories:
            try:
                category = Category(name=name)
                self.valid_records.append(category.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": name, "error": str(e)})

        return pd.DataFrame(self.valid_records)