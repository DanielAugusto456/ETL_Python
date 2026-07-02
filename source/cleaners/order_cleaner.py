import pandas as pd
from .base_cleaner import BaseCleaner
from models.order_model import Order
from config.database import get_creds

COLUMN_MAP = {
    "CustomerID": "customer_id",
    "OrderDate": "order_date",
}

class OrdersCleaner(BaseCleaner):

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.remove_duplicates(data)
        data = self.handle_nulls(data, strategy='drop')

        creds = get_creds()
        statuses_in_db = pd.read_sql_query("SELECT StatusID, StatusName FROM Status", con=creds.engine)
        status_map = dict(zip(statuses_in_db['StatusName'], statuses_in_db['StatusID']))

        data['statusID'] = data['Status'].map(status_map)

        if data['statusID'].isna().any():
            missing_statuses = data[data['statusID'].isna()]['Status'].unique()
            print(f"Estados no encontrados en BD: {missing_statuses}")
            data = data.dropna(subset=['statusID'])

        data['statusID'] = data['statusID'].astype(int)
        data = data.drop(columns=['Status', 'OrderID'], errors='ignore')
        data = data.rename(columns=COLUMN_MAP)

        for _, row in data.iterrows():
            try:
                order = Order(**row.to_dict())
                self.valid_records.append(order.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": row.to_dict(), "error": str(e)})

        return pd.DataFrame(self.valid_records)