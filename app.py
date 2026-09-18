import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from urllib.parse import quote_plus


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Ecommerce Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f5f5f5;
}

.dashboard-title {
    background-color: #ffffff;
    border: 3px solid #3b0b45;
    padding: 12px;
    text-align: center;
    font-size: 30px;
    font-weight: bold;
    color: #111111;
    margin-bottom: 15px;
}

.kpi-card {
    background-color: white;
    padding: 18px;
    border-radius: 8px;
    text-align: center;
    border: 1px solid #dddddd;
}

.kpi-title {
    font-size: 15px;
    color: #666666;
}

.kpi-value {
    font-size: 27px;
    font-weight: bold;
    color: #222222;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="dashboard-title">ECOMMERCE SALES ANALYSIS DASHBOARD</div>',
    unsafe_allow_html=True
)


# =========================================================
# MYSQL CONNECTION
# =========================================================

# Password ko apne MySQL password se replace kar sakte ho.
# @ ko URL me encode karne ke liye quote_plus use kiya gaya hai.

DB_USER = "root"
DB_PASSWORD = "Sanjeet@9973"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "ecommerce"

encoded_password = quote_plus(DB_PASSWORD)

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{encoded_password}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# =========================================================
# LOAD DATA FROM MYSQL
# =========================================================

@st.cache_data
def load_data():

    query = "SELECT * FROM orders"

    data = pd.read_sql(query, engine)

    return data


try:

    df = load_data()

except Exception as e:

    st.error("MySQL database se data load nahi ho raha hai.")

    st.code(str(e))

    st.stop()


# =========================================================
# DATA PREPARATION
# =========================================================

df["Order_Date"] = pd.to_datetime(
    df["Order_Date"],
    errors="coerce"
)

df["Delivery_Date"] = pd.to_datetime(
    df["Delivery_Date"],
    errors="coerce"
)

numeric_columns = [
    "Qty",
    "Unit_Price",
    "Discount",
    "Sales",
    "Net_Amount",
    "Profit"
]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("📊 Dashboard Filters")


# Month

month_order = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]

available_months = [
    month for month in month_order
    if month in df["Month"].dropna().unique()
]

selected_months = st.sidebar.multiselect(
    "Select Month",
    options=available_months,
    default=available_months
)


# City

available_cities = sorted(
    df["City"].dropna().unique()
)

selected_cities = st.sidebar.multiselect(
    "Select City",
    options=available_cities,
    default=available_cities
)


# Payment Mode

available_payment_modes = sorted(
    df["Payment_Mode"].dropna().unique()
)

selected_payment_modes = st.sidebar.multiselect(
    "Payment Mode",
    options=available_payment_modes,
    default=available_payment_modes
)


# Category

available_categories = sorted(
    df["Category"].dropna().unique()
)

selected_categories = st.sidebar.multiselect(
    "Category",
    options=available_categories,
    default=available_categories
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()


if selected_months:

    filtered_df = filtered_df[
        filtered_df["Month"].isin(selected_months)
    ]


if selected_cities:

    filtered_df = filtered_df[
        filtered_df["City"].isin(selected_cities)
    ]


if selected_payment_modes:

    filtered_df = filtered_df[
        filtered_df["Payment_Mode"].isin(selected_payment_modes)
    ]


if selected_categories:

    filtered_df = filtered_df[
        filtered_df["Category"].isin(selected_categories)
    ]


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_sales = filtered_df["Net_Amount"].sum()

total_profit = filtered_df["Profit"].sum()

total_orders = filtered_df["Order_ID"].nunique()

if total_orders > 0:

    average_order_value = (
        total_sales / total_orders
    )

else:

    average_order_value = 0


# =========================================================
# KPI CARDS
# =========================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Sales",
        f"₹{total_sales:,.0f}"
    )


with col2:

    st.metric(
        "Total Profit",
        f"₹{total_profit:,.0f}"
    )


with col3:

    st.metric(
        "Total Orders",
        f"{total_orders:,}"
    )


with col4:

    st.metric(
        "Average Order Value",
        f"₹{average_order_value:,.0f}"
    )


st.divider()


# =========================================================
# ROW 1
# SALES BY MONTH
# =========================================================

monthly_sales = (
    filtered_df
    .groupby("Month", as_index=False)["Net_Amount"]
    .sum()
)

monthly_sales["Month"] = pd.Categorical(
    monthly_sales["Month"],
    categories=month_order,
    ordered=True
)

monthly_sales = monthly_sales.sort_values("Month")


fig_month = px.line(
    monthly_sales,
    x="Month",
    y="Net_Amount",
    markers=True,
    title="Sales by Month"
)

fig_month.update_layout(
    xaxis_title="Month",
    yaxis_title="Sales",
    height=350
)

st.plotly_chart(
    fig_month,
    use_container_width=True
)


# =========================================================
# ROW 2
# CATEGORY + PRODUCT
# =========================================================

col1, col2 = st.columns(2)


# -------------------------
# SALES BY CATEGORY
# -------------------------

with col1:

    category_sales = (
        filtered_df
        .groupby("Category", as_index=False)["Net_Amount"]
        .sum()
        .sort_values(
            "Net_Amount",
            ascending=False
        )
    )

    fig_category = px.bar(
        category_sales,
        x="Category",
        y="Net_Amount",
        title="Sales by Category",
        text_auto=".2s"
    )

    fig_category.update_layout(
        height=350,
        xaxis_title="Category",
        yaxis_title="Sales"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# -------------------------
# SALES BY PRODUCT
# -------------------------

with col2:

    product_sales = (
        filtered_df
        .groupby("Product", as_index=False)["Net_Amount"]
        .sum()
        .sort_values(
            "Net_Amount",
            ascending=False
        )
    )

    fig_product = px.bar(
        product_sales,
        x="Product",
        y="Net_Amount",
        title="Sales by Product",
        text_auto=".2s"
    )

    fig_product.update_layout(
        height=350,
        xaxis_title="Product",
        yaxis_title="Sales"
    )

    st.plotly_chart(
        fig_product,
        use_container_width=True
    )


# =========================================================
# ROW 3
# PAYMENT MODE + ORDER STATUS
# =========================================================

col1, col2 = st.columns(2)


# -------------------------
# PAYMENT MODE
# -------------------------

with col1:

    payment_sales = (
        filtered_df
        .groupby(
            "Payment_Mode",
            as_index=False
        )["Net_Amount"]
        .sum()
    )

    fig_payment = px.pie(
        payment_sales,
        names="Payment_Mode",
        values="Net_Amount",
        hole=0.45,
        title="Sales by Payment Mode"
    )

    fig_payment.update_layout(
        height=380
    )

    st.plotly_chart(
        fig_payment,
        use_container_width=True
    )


# -------------------------
# ORDER STATUS
# -------------------------

with col2:

    status_sales = (
        filtered_df
        .groupby(
            "Order_Status",
            as_index=False
        )["Net_Amount"]
        .sum()
    )

    fig_status = px.pie(
        status_sales,
        names="Order_Status",
        values="Net_Amount",
        title="Sales by Order Status"
    )

    fig_status.update_layout(
        height=380
    )

    st.plotly_chart(
        fig_status,
        use_container_width=True
    )


# =========================================================
# ROW 4
# CITY + PROFIT
# =========================================================

col1, col2 = st.columns(2)


# -------------------------
# SALES BY CITY
# -------------------------

with col1:

    city_sales = (
        filtered_df
        .groupby("City", as_index=False)["Net_Amount"]
        .sum()
        .sort_values(
            "Net_Amount",
            ascending=False
        )
    )

    fig_city = px.bar(
        city_sales,
        x="City",
        y="Net_Amount",
        title="Sales by City",
        text_auto=".2s"
    )

    fig_city.update_layout(
        height=350,
        xaxis_title="City",
        yaxis_title="Sales"
    )

    st.plotly_chart(
        fig_city,
        use_container_width=True
    )


# -------------------------
# PROFIT BY CATEGORY
# -------------------------

with col2:

    profit_category = (
        filtered_df
        .groupby(
            "Category",
            as_index=False
        )["Profit"]
        .sum()
        .sort_values(
            "Profit",
            ascending=False
        )
    )

    fig_profit = px.bar(
        profit_category,
        x="Category",
        y="Profit",
        title="Profit by Category",
        text_auto=".2s"
    )

    fig_profit.update_layout(
        height=350,
        xaxis_title="Category",
        yaxis_title="Profit"
    )

    st.plotly_chart(
        fig_profit,
        use_container_width=True
    )


# =========================================================
# TOP PRODUCTS TABLE
# =========================================================

st.subheader("🏆 Product Sales Summary")


top_products = (
    filtered_df
    .groupby("Product", as_index=False)
    .agg(
        Sales=("Net_Amount", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Qty", "sum")
    )
    .sort_values(
        "Sales",
        ascending=False
    )
)


st.dataframe(
    top_products,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DATA SUMMARY
# =========================================================

with st.expander("View Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Ecommerce Sales Analysis | "
    "Python • Pandas • Plotly • Streamlit • MySQL"
)