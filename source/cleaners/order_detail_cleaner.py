import pandas as pd
from .base_cleaner import BaseCleaner
from models.order_detail_model import OrderDetail

# Mapea las columnas del CSV (PascalCase) a los campos que espera el modelo Pydantic
COLUMN_MAP = {
    "OrderID": "order_id",
    "ProductID": "product_id",
    "Quantity": "quantity",
    "TotalPrice": "totalPrice",
}

class OrderDetailCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.remove_duplicates(data)
        data = self.handle_nulls(data, strategy='drop')
        data = data.rename(columns=COLUMN_MAP)

        for _, row in data.iterrows():
            try:
                order_detail = OrderDetail(**row.to_dict())
                self.valid_records.append(order_detail.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": row.to_dict(), "error": str(e)})

        return pd.DataFrame(self.valid_records)