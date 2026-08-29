import sqlite3

import pandas as pd
import streamlit as st


DB_PATH = "data/transactions.db"

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql(
    "SELECT * FROM transaction_data_cleaned",
    conn
)

conn.close()


st.title("Transaction Data Dashboard")

st.dataframe(df)