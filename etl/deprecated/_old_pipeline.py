import pandas as pd
import sqlite3
import os
from datetime import datetime


country_mapping = {
            "switzerland": "CH",
            "swiss": "CH",
            "schweiz": "CH",
            "suisse": "CH",
            "austria": "AT",
            "österreich": "AT",
            "oesterreich": "AT",
            "germany": "DE",
            "deutschland": "DE",
            "france": "FR",
            "luxembourg": "LU",
            "liechtenstein": "LI",
            "great britain": "GB",
            "england": "GB",
            "uk": "GB",
            "u k": "GB",
            "united kingdom": "GB",
            "italy": "IT",
            "italia": "IT",
            "singapore": "SG",
            "u s a": "US",
            "us": "US",
            "usa": "US",
            "united states": "US",
            "united states of america": "US",
            "ch": "CH",
            "at": "AT",
            "de": "DE",
            "fr": "FR",
            "lu": "LU",
            "li": "LI",
            "gb": "GB",
            "it": "IT",
            "sg": "SG",
            "ger": "DE",
        }

class EtopsPipeline:
    def __init__(self, source_path: str, sql_path: str, table_name: str = 'raw_transaction_data'):
        self.source_path = source_path
        self.sql_path = sql_path
        self.table_name = table_name

    def run_pipeline(self):
        df = self._read_data(self.source_path)
        # NO CLEANING DATA HERE, BUT JUST IN CASE :)
        # df = self._clean_data(df)
        self._load_to_sql(df, sql_path = self.sql_path, table_name = self.table_name)

    def _read_data(self, source_path):
        return pd.read_csv(source_path)

    def _clean_data(self, df: pd.DataFrame):
            df = self._remove_duplicates(df)
            df = self._standardize_to_iso2(df)
            df = self._standardize_risk_profile(df)
            return df

    def _remove_duplicates(self, df: pd.DataFrame):
        return df.drop_duplicates(subset='transaction_id')

    def _standardize_to_iso2(self, df):
        df['client_country'] = (
            df['client_country']
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.lower()
            .str.strip()
        )

        df['client_country'] = df['client_country'].map(country_mapping)
        return df

    def _standardize_risk_profile(df):
        df["risk_profile"] = df['risk_profile'].astype(str).str.lower().str.strip()

        def map_to_standard(profile):
            first_two = profile[:2]
            if first_two == "ag":
                return "aggressive"
            elif first_two == "ba":
                return "balanced"
            elif first_two == "co":
                return "conservative"
            elif first_two == "gr":
                return "growth"
            else:
                return None
        df["risk_profile"] = df["risk_profile"].apply(map_to_standard)
        return df

    def _load_to_sql(self, df: pd.DataFrame, sql_path: str, table_name: str):
        os.makedirs(os.path.dirname(sql_path), exist_ok=True)
        conn = sqlite3.connect(sql_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()

if __name__ == "__main__":
    EtopsPipeline().run_pipeline()
    print(f"Cleaned data loaded to SQLite at {datetime.now()}")
