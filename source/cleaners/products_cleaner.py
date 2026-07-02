import pandas as pd
from .base_cleaner import BaseCleaner
from models.product_model import Product
from config.database import get_creds

class ProductsCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.remove_duplicates(data)
        data = self.handle_nulls(data, strategy='drop')

        creds = get_creds()

        categories_in_db = pd.read_sql_query("SELECT CategoryName FROM category", con=creds.engine)

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

        for _, row in data.iterrows():
            try:
                product = Product(**row.to_dict())
                self.valid_records.append(product.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": row.to_dict(), "error": str(e)})

        return pd.DataFrame(self.valid_records)