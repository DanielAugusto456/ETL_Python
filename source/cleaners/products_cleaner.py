import pandas as pd
from .base_cleaner import BaseCleaner
from models.product_model import Product
from config.database import get_creds

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

        print("\n=== DIAGNÓSTICO DE PRODUCTS CLEANER ===")
        print(f"Columnas disponibles: {data.columns.tolist()}")
        print(f"Total de registros: {len(data)}")
        print(f"Tipos de datos: {data.dtypes}")
        print("================================\n")

        creds = get_creds()

        categories_in_db = pd.read_sql_query(
            "SELECT CategoryID, CategoryName FROM Category", con=creds.engine
        )

        category_map = dict(zip(
            categories_in_db['CategoryName'], 
            categories_in_db['CategoryID']
        ))

        data['Category'] = data['Category'].map(category_map)

        data = data[data['Price'] >= 0]
        data = data[data['Stock'] >= 0]

        if data['Category'].isna().any():
            missing_categories = data[data['Category'].isna()]['Category'].unique()
            print(f"Categorías no encontradas en BD: {missing_categories}")
            data = data.dropna(subset=['Category'])

        data['Category'] = data['Category'].astype(int)

        products_in_db = pd.read_sql_query("SELECT ProductName FROM Products", con=creds.engine)
        product_names_db = set(products_in_db['ProductName'])
        data = self.filter_existing_in_db(data, product_names_db, column='ProductName')

        data = data.drop(columns=['ProductID'], errors='ignore')
        data = data.rename(columns=COLUMN_MAP)

        if data.empty:
            print("No new products to insert.")
            return pd.DataFrame()

        data = data.drop(columns=['ProductID'], errors='ignore')

        for _, row in data.iterrows():
            try:
                product = Product(**row.to_dict())
                self.valid_records.append(product.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": row.to_dict(), "error": str(e)})

        return pd.DataFrame(self.valid_records)