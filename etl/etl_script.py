import pandas as pd
import sqlite3
import os
from datetime import datetime


class EtopsPipeline:
    def __init__(
            self,
            source_path: str = "/opt/airflow/data/raw/transaction_data.csv",
            sql_path: str = "/opt/airflow/data/transactions.db",
            table_name: str = 'raw_transaction_data'
            ):
        self.source_path = source_path
        self.sql_path = sql_path
        self.table_name = table_name

    def run_pipeline(self):
        df = self._read_data(self.source_path)
        self._load_to_sql(df, sql_path = self.sql_path, table_name = self.table_name)

    def _read_data(self, source_path):
        return pd.read_csv(source_path)

    def _load_to_sql(self, df: pd.DataFrame, sql_path: str, table_name: str):
        # os.makedirs(os.path.dirname(sql_path), exist_ok=True)
        conn = sqlite3.connect(sql_path)
        try:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
        finally:
            conn.close()

if __name__ == '__main__':
    EtopsPipeline().run_pipeline()
    print(
        f"Transaction data pipeline completed at {datetime.now()}"
    )
