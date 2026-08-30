import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px

DB_PATH = "data/transactions.db"

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM transaction_data_cleaned", conn)
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
st.bar_chart(top_countries.set_index("client_country")["client_count"])
st.dataframe(top_countries, hide_index=True)

st.subheader("Transactions by Transaction Type")
transaction_types = (
    df["transaction_type"]
    .value_counts()
    .rename_axis("transaction_type")
    .reset_index(name="transaction_count")
)
st.bar_chart(transaction_types.set_index("transaction_type")["transaction_count"])
st.dataframe(transaction_types, hide_index=True)

gross_by_type = (
    df.groupby("transaction_type", as_index=False)["gross_amount_chf"]
    .sum()
    .sort_values("gross_amount_chf", ascending=False)
)
st.subheader("Gross amount by transaction type (CHF)")
fig_gross_type = px.bar(
    gross_by_type,
    x="transaction_type",
    y="gross_amount_chf",
    title="Gross Amount by Transaction Type"
)
st.plotly_chart(fig_gross_type)

fee_by_type = (
    df.groupby("transaction_type", as_index=False)["fee_chf"]
    .sum()
    .sort_values("fee_chf", ascending=False)
)
st.subheader("Fees by transaction type (CHF)")
fig_fee_type = px.bar(
    fee_by_type,
    x="transaction_type",
    y="fee_chf",
    title="Fees by Transaction Type"
)
st.plotly_chart(fig_fee_type)

gross_by_client = (
    df.groupby(["client_id", "client_name"], as_index=False)["gross_amount_chf"]
    .sum()
    .sort_values("gross_amount_chf", ascending=False)
)
st.subheader("Distribution of gross amount by client")
fig_kde, ax = plt.subplots()
gross_by_client["gross_amount_chf"].plot(kind="kde", ax=ax)
ax.set_xlabel("Total gross amount (CHF)")
ax.set_ylabel("Density")
st.pyplot(fig_kde)

# Summary statistics for original data
summary_stats_original = gross_by_client["gross_amount_chf"].describe(
    percentiles=[0.25, 0.5, 0.75]
).rename({
    "25%": "Q1 (25%)",
    "50%": "Median (50%)",
    "75%": "Q3 (75%)"
})
summary_stats_original["Variance"] = gross_by_client["gross_amount_chf"].var()
summary_stats_original = summary_stats_original[["mean", "Variance", "Median (50%)", "min", "max", "Q1 (25%)", "Q3 (75%)"]]

st.subheader("Summary Statistics (Original Data)")
st.dataframe(summary_stats_original.to_frame().T, hide_index=True)

# Filter out the largest observation
client_scatter = gross_by_client.reset_index(drop=True)
client_scatter["client_rank"] = client_scatter.index + 1
client_scatter_filtered = client_scatter[client_scatter["gross_amount_chf"] != client_scatter["gross_amount_chf"].max()]

# Summary statistics for filtered data
summary_stats_filtered = client_scatter_filtered["gross_amount_chf"].describe(
    percentiles=[0.25, 0.5, 0.75]
).rename({
    "25%": "Q1 (25%)",
    "50%": "Median (50%)",
    "75%": "Q3 (75%)"
})
summary_stats_filtered["Variance"] = client_scatter_filtered["gross_amount_chf"].var()
summary_stats_filtered = summary_stats_filtered[["mean", "Variance", "Median (50%)", "min", "max", "Q1 (25%)", "Q3 (75%)"]]

st.subheader("Summary Statistics (Largest Observation Removed)")
st.dataframe(summary_stats_filtered.to_frame().T, hide_index=True)

# Scatter plots
st.subheader("Gross amount by client")
fig_scatter = px.scatter(
    client_scatter,
    x="client_rank",
    y="gross_amount_chf",
    title="Gross Amount by Client Rank"
)
st.plotly_chart(fig_scatter)

st.subheader("Gross amount by client (largest observation removed)")
fig_scatter_filtered = px.scatter(
    client_scatter_filtered,
    x="client_rank",
    y="gross_amount_chf",
    title="Gross Amount by Client Rank (Largest Observation Removed)"
)
st.plotly_chart(fig_scatter_filtered)

# Bar chart: Gross amount (CHF) per asset class (all countries)
st.subheader("Gross amount (CHF) per asset class")
gross_by_asset_class = (
    df.groupby("asset_class", as_index=False)["gross_amount_chf"]
    .sum()
    .sort_values("gross_amount_chf", ascending=False)
)
fig_asset_class_gross = px.bar(
    gross_by_asset_class,
    x="asset_class",
    y="gross_amount_chf",
    title="Gross Amount (CHF) by Asset Class"
)
st.plotly_chart(fig_asset_class_gross)

# Bar chart: Gross amount (CHF) per asset class (CH only)
st.subheader("Gross amount (CHF) per asset class (Switzerland only)")
gross_by_asset_class_ch = (
    df[df["client_country"] == "CH"]
    .groupby("asset_class", as_index=False)["gross_amount_chf"]
    .sum()
    .sort_values("gross_amount_chf", ascending=False)
)
fig_asset_class_ch = px.bar(
    gross_by_asset_class_ch,
    x="asset_class",
    y="gross_amount_chf",
    title="Gross Amount (CHF) by Asset Class (Switzerland Only)"
)
st.plotly_chart(fig_asset_class_ch)

# Transactions by asset class
asset_class_counts = (
    df["asset_class"]
    .value_counts()
    .rename_axis("asset_class")
    .reset_index(name="count")
)
st.subheader("Transactions by asset class")
fig_asset_class = px.bar(
    asset_class_counts,
    x="asset_class",
    y="count",
    title="Transactions by Asset Class"
)
st.plotly_chart(fig_asset_class)
st.dataframe(asset_class_counts, hide_index=True)