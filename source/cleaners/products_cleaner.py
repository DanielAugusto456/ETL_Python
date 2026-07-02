import pandas as pd
from .base_cleaner import BaseCleaner
from models.product_model import Product
from config.database import get_creds

# Mapea las columnas del CSV (PascalCase) a los campos que espera el modelo Pydantic
COLUMN_MAP = {
    "ProductName": "name",
    "Category": "categoryID",
    "Price": "price",
    "Stock": "stock",
}

class ProductsCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.remove_duplicates(data)
        data = self.handle_nulls(data, strategy='drop')

        creds = get_creds()

        # El SELECT original no traía CategoryID, y luego se usaba más abajo (KeyError)
        categories_in_db = pd.read_sql_query(
            "SELECT CategoryID, CategoryName FROM category", con=creds.engine
        )

        category_map = dict(zip(
            categories_in_db['CategoryName'], 
            categories_in_db['CategoryID']
        ))

        data['Category'] = data['Category'].map(category_map)

        if data['Category'].isna().any():
            missing_categories = data[data['Category'].isna()]['Category'].unique()
            print(f"Categorías no encontradas en BD: {missing_categories}")
            data = data.dropna(subset=['Category'])

        data['Category'] = data['Category'].astype(int)

        # Descartar productos cuyo nombre ya existe en BD (evita duplicados en re-cargas)
        products_in_db = pd.read_sql_query("SELECT ProductName FROM Product", con=creds.engine)
        product_names_db = set(products_in_db['ProductName'])
        data = self.filter_existing_in_db(data, product_names_db, column='ProductName')

        if data.empty:
            print("No new products to insert.")
            return pd.DataFrame()

        data = data.drop(columns=['ProductID'], errors='ignore')
        data = data.rename(columns=COLUMN_MAP)

        for _, row in data.iterrows():
            try:
                product = Product(**row.to_dict())
                self.valid_records.append(product.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": row.to_dict(), "error": str(e)})

        return pd.DataFrame(self.valid_records)