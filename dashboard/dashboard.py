import sqlite3

import pandas as pd
import streamlit as st


DB_PATH = "data/transactions.db"


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        "SELECT * FROM transaction_data_cleaned",
        conn,
    )

    conn.close()

    return df


df = load_data()

st.title("Transaction Data Dashboard")

st.subheader("Top 10 Countries by Number of Clients")

top_countries = (
    df.groupby("client_country")["client_id"]
    .nunique()
    .sort_values(ascending=False)
    .head(10)
    .reset_index(name="client_count")
)

st.bar_chart(
    top_countries.set_index("client_country")["client_count"]
)

st.dataframe(
    top_countries,
    hide_index=True,
)


st.subheader("Transactions by Transaction Type")

transaction_types = (
    df["transaction_type"]
    .value_counts()
    .rename_axis("transaction_type")
    .reset_index(name="transaction_count")
)

st.bar_chart(
    transaction_types.set_index("transaction_type")["transaction_count"]
)

st.dataframe(
    transaction_types,
    hide_index=True,
)