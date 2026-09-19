import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="SkyCity Auckland Restaurant Dashboard",
    page_icon="🍽️",
    layout="wide"
)

# Find the Excel dataset in the repository
possible_files = [
    "SkyCity_Auckland_Restaurants_Bars_Excel_Project(2).xlsx",
    "SkyCity_Auckland_Restaurants_Bars_Excel_Project.xlsx",
    "SkyCity_Auckland_Restaurants_Bars_Excel_Project(1).xlsx",
]

data_file = next((f for f in possible_files if Path(f).exists()), None)

if data_file is None:
    st.error("Excel dataset not found. Upload the SkyCity Excel file to the same GitHub repository as app.py.")
    st.stop()

# Read the calculated data sheet
df = pd.read_excel(data_file, sheet_name="Calculated_Data")

# Convert important numeric columns
numeric_cols = [
    "AOV", "MonthlyOrders", "InStoreOrders", "UberEatsOrders",
    "DoorDashOrders", "SelfDeliveryOrders", "InStoreRevenue",
    "UberEatsRevenue", "DoorDashRevenue", "SelfDeliveryRevenue",
    "Total Revenue", "Total Orders", "Delivery Orders",
    "Total Net Profit", "Profit Margin"
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

st.title("🍽️ SkyCity Auckland Restaurants & Bars")
st.caption("Interactive restaurant performance dashboard")

# Sidebar filters
filtered = df.copy()
st.sidebar.header("Filters")

for col, label in [
    ("CuisineType", "Cuisine"),
    ("Segment", "Segment"),
    ("Subregion", "Subregion")
]:
    if col in df.columns:
        choices = st.sidebar.multiselect(
            label,
            sorted(df[col].dropna().astype(str).unique())
        )
        if choices:
            filtered = filtered[filtered[col].astype(str).isin(choices)]

# KPI cards
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Restaurants", f"{filtered['RestaurantID'].nunique():,}")
c2.metric("Monthly Orders", f"{filtered['MonthlyOrders'].sum():,.0f}")
c3.metric("Revenue", f"${filtered['Total Revenue'].sum():,.2f}")
c4.metric("Net Profit", f"${filtered['Total Net Profit'].sum():,.2f}")
c5.metric("Average AOV", f"${filtered['AOV'].mean():,.2f}")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Cuisine", "Delivery", "Profitability"]
)

with tab1:
    st.subheader("Top Restaurants by Revenue")
    top = (
        filtered.groupby("RestaurantName", as_index=False)
        .agg(
            Revenue=("Total Revenue", "sum"),
            Profit=("Total Net Profit", "sum"),
            Orders=("MonthlyOrders", "sum")
        )
        .sort_values("Revenue", ascending=False)
        .head(10)
    )
    st.bar_chart(top.set_index("RestaurantName")[["Revenue", "Profit"]])
    st.dataframe(top, use_container_width=True)

with tab2:
    st.subheader("Performance by Cuisine")
    x = (
        filtered.groupby("CuisineType", as_index=False)
        .agg(
            Restaurants=("RestaurantID", "nunique"),
            Orders=("MonthlyOrders", "sum"),
            Revenue=("Total Revenue", "sum"),
            Profit=("Total Net Profit", "sum")
        )
        .sort_values("Revenue", ascending=False)
    )
    st.bar_chart(x.set_index("CuisineType")[["Revenue", "Profit"]])
    st.dataframe(x, use_container_width=True)

with tab3:
    st.subheader("Delivery Channel Performance")

    revenue_cols = {
        "Uber Eats": "UberEatsRevenue",
        "DoorDash": "DoorDashRevenue",
        "Self Delivery": "SelfDeliveryRevenue"
    }
    order_cols = {
        "Uber Eats": "UberEatsOrders",
        "DoorDash": "DoorDashOrders",
        "Self Delivery": "SelfDeliveryOrders"
    }

    rev = {
        k: filtered[v].sum()
        for k, v in revenue_cols.items()
        if v in filtered.columns
    }
    orders = {
        k: filtered[v].sum()
        for k, v in order_cols.items()
        if v in filtered.columns
    }

    if rev:
        st.write("Delivery Revenue")
        st.bar_chart(pd.Series(rev, name="Revenue"))

    if orders:
        st.write("Delivery Orders")
        st.bar_chart(pd.Series(orders, name="Orders"))

with tab4:
    st.subheader("Profitability by Restaurant")

    x = (
        filtered.groupby("RestaurantName", as_index=False)
        .agg(
            Revenue=("Total Revenue", "sum"),
            Profit=("Total Net Profit", "sum")
        )
    )

    x["ProfitMargin"] = np.where(
        x["Revenue"] != 0,
        x["Profit"] / x["Revenue"] * 100,
        0
    )

    x = x.sort_values("Profit", ascending=False)

    st.bar_chart(
        x.head(10).set_index("RestaurantName")["Profit"]
    )
    st.dataframe(x, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption(f"Dataset: {data_file}")
