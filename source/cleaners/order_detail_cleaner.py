import pandas as pd
from .base_cleaner import BaseCleaner
from models.order_detail_model import OrderDetail
from config.database import get_creds

COLUMN_MAP = {
    "OrderID": "order_id",
    "ProductID": "product_id",
    "Quantity": "quantity",
    "TotalPrice": "total_price",
}

class OrderDetailCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.remove_duplicates(data)
        data = self.handle_nulls(data, strategy='drop')
        data = data.rename(columns=COLUMN_MAP)

        if data.empty:
            print("No order details to process.")
            return pd.DataFrame()

        creds = get_creds()

        if 'order_id' in data.columns and not data.empty:
            orders_in_db = pd.read_sql_query(
                "SELECT OrderID FROM Orders",
                con=creds.engine
            )
            valid_order_ids = set(orders_in_db['OrderID'].tolist())
            before = len(data)
            data = data[data['order_id'].isin(valid_order_ids)]
            removed = before - len(data)
            if removed:
                print(f"{removed} registros descartados por OrderID no existente")

        if 'product_id' in data.columns and not data.empty:
            products_in_db = pd.read_sql_query(
                "SELECT ProductID FROM Products",
                con=creds.engine
            )
            valid_product_ids = set(products_in_db['ProductID'].tolist())
            before = len(data)
            data = data[data['product_id'].isin(valid_product_ids)]
            removed = before - len(data)
            if removed:
                print(f"{removed} registro(s) descartado(s) por ProductID no existente")

        if not data.empty:
            data = data[data['quantity'] > 0]
            data = data[data['total_price'] >= 0]
            data = data[data['order_id'] > 0]
            data = data[data['product_id'] > 0]

        if data.empty:
            print("No valid order details to insert.")
            return pd.DataFrame()

        for _, row in data.iterrows():
            try:
                order_detail = OrderDetail(**row.to_dict())
                self.valid_records.append(order_detail.model_dump())
            except Exception as e:
                self.invalid_records.append({
                    "record": row.to_dict(),
                    "error": str(e)
                })
                print(f"Registro inválido: {e}")

        if not self.valid_records:
            print("No valid order details to insert.")
            return pd.DataFrame()

        print(f"{len(self.valid_records)} registro(s) válido(s) para cargar en 'OrderDetail'.")
        return pd.DataFrame(self.valid_records)