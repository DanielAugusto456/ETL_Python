import logging
from abc import ABC, abstractmethod
from typing import Dict

import pandas as pd
from bcpandas import to_sql

from config.database import get_creds

class SqlServerLoader(ABC):

    schema: str = "dbo"
    column_map: Dict[str, str] = {}

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def table_name(self) -> str:
        raise NotImplementedError

    def prepare(self, data: pd.DataFrame) -> pd.DataFrame:
        if self.column_map:
            data = data.rename(columns=self.column_map)
        return data

    def load(self, data: pd.DataFrame, identity_insert: bool = False) -> None:
        if data is None or data.empty:
            self.logger.info(f"No hay registros nuevos para cargar en '{self.table_name}'.")
            return

        data = self.prepare(data)
        creds = get_creds()

        try:
            to_sql(
                df=data,
                table_name=self.table_name,
                creds=creds,
                schema=self.schema,
                index=False,
                if_exists="append",
                identity_insert=identity_insert,
            )
            self.logger.info(
                f"{len(data)} registro(s) cargado(s) en '{self.schema}.{self.table_name}'."
            )
        except Exception as e:
            self.logger.error(f"Error cargando datos en '{self.table_name}': {e}")
            raise
