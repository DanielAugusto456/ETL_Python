import pandas as pd
from .base_cleaner import BaseCleaner
from models.category_model import Category
from config.database import get_creds

class CategoryCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        # 1. Aislar y limpiar la columna de categorías del origen (p. ej. products.csv)
        categories = data["Category"].astype(str).str.strip()
        categories = self.remove_duplicates(categories)
        categories = self.handle_nulls(categories, strategy='drop')
        categories = categories[categories != ""]

        # 2. Traer las categorías que ya existen en BD
        creds = get_creds()
        categories_in_db = pd.read_sql_query(
            "SELECT CategoryName FROM Category", con=creds.engine
        )
        categories_db = set(categories_in_db['CategoryName'])

        # 3. Quedarnos solo con las categorías nuevas (que no están en BD)
        new_categories = self.filter_existing_in_db(categories, categories_db)

        if new_categories.empty:
            print("No new categories to insert.")
            return pd.DataFrame()

        # 4. Validar cada categoría nueva con el modelo Pydantic
        for name in new_categories:
            try:
                category = Category(name=name)
                self.valid_records.append(category.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": name, "error": str(e)})

        return pd.DataFrame(self.valid_records)