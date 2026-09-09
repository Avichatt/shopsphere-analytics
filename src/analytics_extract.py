import os
import urllib.parse
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

load_dotenv()

# Database connection
DB_USER = os.getenv("DB_USER")
DB_PASS = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))  # escape special chars
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

connection_string = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(connection_string)


query = """
SELECT
    f.order_id,
    f.order_item_id,
    f.customer_key,
    f.product_key,
    f.seller_key,
    f.date_key,
    f.quantity,
    f.unit_price,
    f.freight_value,
    f.sales_amount,

    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,

    c.customer_unique_id,
    c.customer_city,
    c.customer_state,

    p.product_category_name_english AS product_category,

    s.seller_city,
    s.seller_state

FROM analytics.fact_sales f

JOIN analytics.dim_order o
    ON f.order_key = o.order_key

JOIN analytics.dim_customer c
    ON f.customer_key = c.customer_key

JOIN analytics.dim_product p
    ON f.product_key = p.product_key

JOIN analytics.dim_seller s
    ON f.seller_key = s.seller_key;
"""


df = pd.read_sql(query, engine)

customer_df = (
    df.groupby("customer_unique_id")
    .agg(
        total_orders=("order_id", "nunique"),
        total_items=("quantity", "sum"),
        total_revenue=("sales_amount", "sum"),
        total_freight=("freight_value", "sum"),
        first_order_date=("order_purchase_timestamp", "min"),
        last_order_date=("order_purchase_timestamp", "max")
    )
    .reset_index()
)

print("\n" + "=" * 80)
print("CUSTOMER-LEVEL DATASET")
print("=" * 80)

print(f"Rows: {customer_df.shape[0]}")
print(f"Columns: {customer_df.shape[1]}")

print("\n--- CUSTOMER DATA ---")
print(customer_df.head(10))


# Group and aggregate customer-level metrics
customer_summary = (
    df.groupby("customer_unique_id")
      .agg(
          total_orders=("order_id", "nunique"),
          total_items=("quantity", "sum"),
          total_revenue=("sales_amount", "sum"),
          first_order_date=("order_purchase_timestamp", "min"),
          last_order_date=("order_purchase_timestamp", "max")
      )
      .reset_index()
)

print(customer_summary.head())




analysis_date = customer_summary["last_order_date"].max() + pd.Timedelta(days=1)
customer_df["recency"] = (analysis_date - customer_df["last_order_date"]).dt.days
customer_df["frequency"] = customer_df["total_orders"]
customer_df["monetary"] = customer_df["total_revenue"]

rfm_df = customer_df[["customer_unique_id", "recency", "frequency", "monetary"]].copy()
print("\n" + "=" * 80)
print("RFM DATASET")
print("=" * 80)
print(rfm_df.head(10))



# Calculate RFM scores
rfm_df["r_score"] = pd.qcut(rfm_df["recency"], q=5, labels=[5, 4, 3, 2, 1])
rfm_df["f_score"] = pd.qcut(rfm_df["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])
rfm_df["m_score"] = pd.qcut(rfm_df["monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])

# Combine into total RFM score
rfm_df["rfm_score"] = (
    rfm_df["r_score"].astype(int)
    + rfm_df["f_score"].astype(int)
    + rfm_df["m_score"].astype(int)
)

# Display results
print("\n" + "=" * 80)
print("RFM SCORES")
print("=" * 80)
print(
    rfm_df[
        [
            "customer_unique_id",
            "recency",
            "frequency",
            "monetary",
            "r_score",
            "f_score",
            "m_score",
            "rfm_score"
        ]
    ].head(20)
)

# Define segmentation logic
def assign_segment(row):
    if row["r_score"] >= 4 and row["f_score"] >= 4 and row["m_score"] >= 4:
        return "Champions"
    elif row["r_score"] >= 4 and row["f_score"] >= 3:
        return "Loyal Customers"
    elif row["r_score"] >= 4 and row["f_score"] <= 2:
        return "Recent Customers"
    elif row["r_score"] <= 2 and row["f_score"] >= 3:
        return "At Risk"
    elif row["r_score"] <= 2 and row["f_score"] <= 2:
        return "Inactive"
    else:
        return "Potential Loyalists"

# Apply segmentation
rfm_df["customer_segment"] = rfm_df.apply(assign_segment, axis=1)

# Save customer RFM segmentation to PostgreSQL
rfm_df.to_sql(
    "customer_rfm",
    engine,
    schema="analytics",
    if_exists="replace",
    index=False
)

print("Customer RFM table successfully saved to PostgreSQL.")

# Summarize segments
print("\n" + "=" * 80)
print("CUSTOMER SEGMENTS")
print("=" * 80)

segment_summary = (
    rfm_df["customer_segment"]
    .value_counts()
    .rename_axis("customer_segment")
    .reset_index(name="customer_count")
)

print(segment_summary)



clv_df = (
    rfm_df
    .groupby("customer_unique_id")
    .agg(
        total_revenue=("monetary", "sum"),
        total_orders=("frequency", "sum"),
        recency_days=("recency", "min")
    )
    .reset_index()
)

clv_df["average_order_value"] = (
    clv_df["total_revenue"]
    / clv_df["total_orders"]
)

print("\n" + "=" * 80)
print("CUSTOMER LIFETIME VALUE")
print("=" * 80)

print(
    clv_df.sort_values(
        "total_revenue",
        ascending=False
    ).head(20)
)

print(
    clv_df[
        [
            "total_revenue",
            "total_orders",
            "average_order_value"
        ]
    ].describe()
)

segment_value_df = (
    rfm_df
    .merge(
        clv_df[
            [
                "customer_unique_id",
                "total_revenue",
                "total_orders",
                "average_order_value"
            ]
        ],
        on="customer_unique_id",
        how="left"
    )
    .groupby("customer_segment")
    .agg(
        customer_count=("customer_unique_id", "nunique"),
        total_revenue=("total_revenue", "sum"),
        total_orders=("total_orders", "sum"),
        average_customer_revenue=("total_revenue", "mean"),
        average_order_value=("average_order_value", "mean")
    )
    .reset_index()
    .sort_values(
        "total_revenue",
        ascending=False
    )
)

print("\n" + "=" * 80)
print("CUSTOMER SEGMENT VALUE ANALYSIS")
print("=" * 80)

print(segment_value_df)


# Delivery Performance Analysis

# delivery_df = df[
#     [
#         "order_id",
#         "order_purchase_timestamp",
#         "order_delivered_customer_date"
#     ]
# ].drop_duplicates("order_id").copy()

# delivery_df["delivery_days"] = (
#     delivery_df["order_delivered_customer_date"]
#     - delivery_df["order_purchase_timestamp"]
# ).dt.total_seconds() / (60 * 60 * 24)

# print("\n" + "=" * 80)
# print("DELIVERY PERFORMANCE")
# print("=" * 80)

# print(
#     delivery_df["delivery_days"].describe()
# )

# # Calculate average delivery time
# average_delivery_days = (
#     delivery_df["delivery_days"]
#     .mean()
# )

# print(
#     f"Average delivery time: "
#     f"{average_delivery_days:.2f} days"
# )




# # On-Time vs Late Delivery
# # delivery_df = df[
# #     [
# #         "order_id",
# #         "order_purchase_timestamp",
# #         "order_delivered_customer_date",
# #         "order_estimated_delivery_date"
# #     ]
# # ].drop_duplicates("order_id").copy()

# # delivery_df["delivery_days"] = (
# #     delivery_df["order_delivered_customer_date"]
# #     - delivery_df["order_purchase_timestamp"]
# # ).dt.total_seconds() / (60 * 60 * 24)

# # delivery_df["delivery_status"] = delivery_df.apply(
# #     lambda row:
# #         "Unknown"
# #         if pd.isna(row["order_delivered_customer_date"])
# #         or pd.isna(row["order_estimated_delivery_date"])
# #         else (
# #             "On Time"
# #             if row["order_delivered_customer_date"]
# #             <= row["order_estimated_delivery_date"]
# #             else "Late"
# #         ),
# #     axis=1
# # )

# # print("\n" + "=" * 80)
# # print("ON-TIME VS LATE DELIVERY")
# # print("=" * 80)

# # print(
# #     delivery_df["delivery_status"]
# #     .value_counts()
# # )

# # print("\nPercentage:")
# # print(
# #     delivery_df["delivery_status"]
# #     .value_counts(normalize=True)
# #     .mul(100)
# #     .round(2)
# # )


# # Delivery Delay Analysis

# # delivery_df["delay_days"] = (
# #     delivery_df["order_delivered_customer_date"]
# #     - delivery_df["order_estimated_delivery_date"]
# # ).dt.total_seconds() / (60 * 60 * 24)

# # late_orders = delivery_df[
# #     delivery_df["delivery_status"] == "Late"
# # ].copy()

# # print("\n" + "=" * 80)
# # print("DELIVERY DELAY ANALYSIS")
# # print("=" * 80)

# # print(f"Late orders: {len(late_orders)}")

# # print("\nDelay statistics:")
# # print(
# #     late_orders["delay_days"].describe()
# # )

# # print(
# #     f"\nAverage delay: "
# #     f"{late_orders['delay_days'].mean():.2f} days"
# # )

# # print(
# #     f"Maximum delay: "
# #     f"{late_orders['delay_days'].max():.2f} days"
# # )


# # Review & Rating Analysis

# review_query = """
# SELECT
#     r.review_id,
#     r.order_id,
#     r.review_score,
#     r.review_comment_title,
#     r.review_comment_message,
#     r.review_creation_date,
#     r.review_answer_timestamp,
#     r.customer_key,
#     c.customer_city,
#     c.customer_state

# FROM analytics.fact_reviews r

# JOIN analytics.dim_customer c
#     ON r.customer_key = c.customer_key;
# """

# review_df = pd.read_sql(review_query, engine)

# print("\n" + "=" * 80)
# print("REVIEW & RATING ANALYSIS")
# print("=" * 80)

# print("\nReview dataset:")
# print(review_df.head())

# print("\nOverall review statistics:")
# print(
#     review_df["review_score"].describe()
# )

# print("\nReview score distribution:")
# print(
#     review_df["review_score"]
#     .value_counts()
#     .sort_index()
# )




# # Review Performance by Customer State

# state_review_df = (
#     review_df
#     .groupby("customer_state")
#     .agg(
#         review_count=("review_id", "nunique"),
#         average_rating=("review_score", "mean")
#     )
#     .reset_index()
# )

# state_review_df["average_rating"] = (
#     state_review_df["average_rating"]
#     .round(2)
# )

# state_review_df["review_percentage"] = (
#     state_review_df["review_count"]
#     / state_review_df["review_count"].sum()
#     * 100
# ).round(2)

# state_review_df = state_review_df.sort_values(
#     "average_rating",
#     ascending=False
# )

# print("\n" + "=" * 80)
# print("REVIEW PERFORMANCE BY CUSTOMER STATE")
# print("=" * 80)

# print(state_review_df)

# # Revenue Concentration Analysis

# customer_revenue_df = (
#     customer_df[
#         [
#             "customer_unique_id",
#             "total_revenue"
#         ]
#     ]
#     .copy()
#     .sort_values(
#         "total_revenue",
#         ascending=False
#     )
# )

# customer_revenue_df["cumulative_revenue"] = (
#     customer_revenue_df["total_revenue"]
#     .cumsum()
# )

# total_revenue = (
#     customer_revenue_df["total_revenue"].sum()
# )

# customer_revenue_df["cumulative_revenue_percentage"] = (
#     customer_revenue_df["cumulative_revenue"]
#     / total_revenue
#     * 100
# )

# customer_revenue_df["customer_percentage"] = (
#     (customer_revenue_df.index + 1)
#     / len(customer_revenue_df)
#     * 100
# )

# print("\n" + "=" * 80)
# print("REVENUE CONCENTRATION ANALYSIS")
# print("=" * 80)

# print("\nTop customers by revenue:")
# print(
#     customer_revenue_df.head(20)
# )

# # calculate the top 20% contribution
# top_20_count = int(
#     len(customer_revenue_df) * 0.20
# )

# top_20_revenue = (
#     customer_revenue_df
#     .head(top_20_count)["total_revenue"]
#     .sum()
# )

# top_20_percentage = (
#     top_20_revenue
#     / total_revenue
#     * 100
# )

# print(
#     f"\nTop 20% of customers generate "
#     f"{top_20_percentage:.2f}% of total revenue."
# )


# # Revenue by Customer Segment
# segment_revenue_df = (
#     rfm_df
#     .groupby("customer_segment")
#     .agg(
#         customer_count=("customer_unique_id", "nunique"),
#         total_revenue=("monetary", "sum"),
#         average_revenue=("monetary", "mean"),
#         average_frequency=("frequency", "mean"),
#         average_recency=("recency", "mean")
#     )
#     .reset_index()
# )

# segment_revenue_df["revenue_percentage"] = (
#     segment_revenue_df["total_revenue"]
#     / segment_revenue_df["total_revenue"].sum()
#     * 100
# ).round(2)

# segment_revenue_df["average_revenue"] = (
#     segment_revenue_df["average_revenue"]
#     .round(2)
# )

# segment_revenue_df["average_frequency"] = (
#     segment_revenue_df["average_frequency"]
#     .round(2)
# )

# segment_revenue_df["average_recency"] = (
#     segment_revenue_df["average_recency"]
#     .round(2)
# )

# segment_revenue_df = segment_revenue_df.sort_values(
#     "total_revenue",
#     ascending=False
# )

# print("\n" + "=" * 80)
# print("REVENUE BY CUSTOMER SEGMENT")
# print("=" * 80)

# print(segment_revenue_df)


# # Product & Category Performance Analysis

# product_performance_df = (
#     df
#     .groupby(
#         [
#             "product_key",
#             "product_category"
#         ]
#     )
#     .agg(
#         units_sold=("quantity", "sum"),
#         total_revenue=("sales_amount", "sum"),
#         average_unit_price=("unit_price", "mean")
#     )
#     .reset_index()
# )

# product_performance_df["average_unit_price"] = (
#     product_performance_df["average_unit_price"]
#     .round(2)
# )

# product_performance_df = (
#     product_performance_df
#     .sort_values(
#         "total_revenue",
#         ascending=False
#     )
# )

# print("\n" + "=" * 80)
# print("PRODUCT PERFORMANCE")
# print("=" * 80)

# print("\nTop products by revenue:")
# print(
#     product_performance_df.head(20)
# )

# # analyze categories
# category_performance_df = (
#     product_performance_df
#     .groupby("product_category")
#     .agg(
#         product_count=("product_key", "nunique"),
#         units_sold=("units_sold", "sum"),
#         total_revenue=("total_revenue", "sum"),
#         average_product_price=("average_unit_price", "mean")
#     )
#     .reset_index()
#     .sort_values(
#         "total_revenue",
#         ascending=False
#     )
# )

# category_performance_df["average_product_price"] = (
#     category_performance_df["average_product_price"]
#     .round(2)
# )

# print("\n" + "=" * 80)
# print("CATEGORY PERFORMANCE")
# print("=" * 80)

# print(
#     category_performance_df.head(20)
# )


# # Revenue Anomaly Detection

# daily_revenue_df = (
#     df
#     .assign(
#         order_date=df["order_purchase_timestamp"].dt.date
#     )
#     .groupby("order_date")
#     .agg(
#         total_revenue=("sales_amount", "sum"),
#         total_orders=("order_id", "nunique")
#     )
#     .reset_index()
# )

# daily_revenue_df["total_revenue"] = (
#     daily_revenue_df["total_revenue"]
#     .astype(float)
# )

# mean_revenue = daily_revenue_df["total_revenue"].mean()
# std_revenue = daily_revenue_df["total_revenue"].std()

# daily_revenue_df["z_score"] = (
#     daily_revenue_df["total_revenue"] - mean_revenue
# ) / std_revenue

# daily_revenue_df["anomaly"] = (
#     daily_revenue_df["z_score"].abs() >= 3
# )

# print("\n" + "=" * 80)
# print("REVENUE ANOMALY DETECTION")
# print("=" * 80)

# print(f"Average daily revenue: {mean_revenue:.2f}")
# print(f"Revenue standard deviation: {std_revenue:.2f}")

# print("\nAnomalous days:")
# print(
#     daily_revenue_df[
#         daily_revenue_df["anomaly"]
#     ]
#     .sort_values(
#         "total_revenue",
#         ascending=False
#     )
# )


# # Revenue Trend & Forecasting

# monthly_revenue_df = (
#     df
#     .assign(
#         order_month=df["order_purchase_timestamp"].dt.to_period("M")
#     )
#     .groupby("order_month")
#     .agg(
#         total_revenue=("sales_amount", "sum"),
#         total_orders=("order_id", "nunique")
#     )
#     .reset_index()
# )

# monthly_revenue_df["order_month"] = (
#     monthly_revenue_df["order_month"]
#     .dt.to_timestamp()
# )

# monthly_revenue_df["revenue_3m_avg"] = (
#     monthly_revenue_df["total_revenue"]
#     .rolling(window=3)
#     .mean()
# )

# print("\n" + "=" * 80)
# print("MONTHLY REVENUE TREND & FORECAST")
# print("=" * 80)

# print(monthly_revenue_df)

# # create the next month's forecast
# last_month = monthly_revenue_df["order_month"].max()

# next_month = (
#     last_month
#     + pd.DateOffset(months=1)
# )

# forecast_value = (
#     monthly_revenue_df["total_revenue"]
#     .tail(3)
#     .mean()
# )

# print(l
#     f"\nForecast month: "
#     f"{next_month.strftime('%Y-%m')}"
# )

# print(
#     f"Forecast revenue: "
#     f"{forecast_value:.2f}"
# )
