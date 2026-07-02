import pandas as pd
from .base_cleaner import BaseCleaner
from models.status_model import Status
from config.database import get_creds
from normalizer import normalizer

class StatusCleaner(BaseCleaner):
    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data["Status"].copy()

        data = self.remove_duplicates(data)
        data = self.handle_nulls(data, strategy='drop')

        creds = get_creds()

        statuses_in_db = pd.read_sql_query("SELECT name FROM Status", con=creds.engine)

        statuses_db = set(statuses_in_db['StatusName'])

        data = data[~data.isin(statuses_db)]

        if data.empty:
            print("No new statuses to insert.")
            return pd.DataFrame()

        for _, row in data.iterrows():
            try:
                status = Status(**row.to_dict())
                self.valid_records.append(status.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": row.to_dict(), "error": str(e)})

        return pd.DataFrame(self.valid_records)