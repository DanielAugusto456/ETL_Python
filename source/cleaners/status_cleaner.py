import pandas as pd
from .base_cleaner import BaseCleaner
from models.status_model import Status
from config.database import get_creds

class StatusCleaner(BaseCleaner):
    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        # 1. Aislar y limpiar la columna de estados del origen (p. ej. orders.csv)
        statuses = data["Status"].astype(str).str.strip()
        statuses = self.remove_duplicates(statuses)
        statuses = self.handle_nulls(statuses, strategy='drop')
        statuses = statuses[statuses != ""]

        # 2. Traer los estados que ya existen en BD
        creds = get_creds()
        statuses_in_db = pd.read_sql_query("SELECT name FROM Status", con=creds.engine)
        statuses_db = set(statuses_in_db['name'])

        # 3. Quedarnos solo con los estados nuevos (que no están en BD)
        new_statuses = self.filter_existing_in_db(statuses, statuses_db)

        if new_statuses.empty:
            print("No new statuses to insert.")
            return pd.DataFrame()

        # 4. Validar cada estado nuevo con el modelo Pydantic
        for name in new_statuses:
            try:
                status = Status(name=name)
                self.valid_records.append(status.model_dump())
            except Exception as e:
                self.invalid_records.append({"record": name, "error": str(e)})

        return pd.DataFrame(self.valid_records)