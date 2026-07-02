import pandas as pd
from .base_cleaner import BaseCleaner
from models.status_model import Status
from config.database import get_creds

class StatusCleaner(BaseCleaner):
    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        statuses = data["Status"].astype(str).str.strip()
        statuses = self.remove_duplicates(statuses)
        statuses = self.handle_nulls(statuses, strategy='drop')
        statuses = statuses[statuses != ""]

        creds = get_creds()
        statuses_in_db = pd.read_sql_query("SELECT StatusName FROM Status", con=creds.engine)
        statuses_db = set(statuses_in_db['StatusName'])

        new_statuses = self.filter_existing_in_db(statuses, statuses_db)

        if new_statuses.empty:
            print("No new statuses to insert.")
            return pd.DataFrame()

        for name in new_statuses:
            try:
                status = Status(name=name)
                self.valid_records.append(status.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": name, "error": str(e)})

        return pd.DataFrame(self.valid_records)