import pandas as pd

# ===================================================
# LOAD DATASETS
# ===================================================

customers = pd.read_csv("data/olist_customers_dataset.csv")

orders = pd.read_csv(
    "data/olist_orders_dataset.csv",
    parse_dates=[
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
)

order_items = pd.read_csv("data/olist_order_items_dataset.csv")

payments = pd.read_csv("data/olist_order_payments_dataset.csv")

reviews = pd.read_csv("data/olist_order_reviews_dataset.csv")

# ===================================================
# SELECT IMPORTANT COLUMNS
# ===================================================

customers = customers[
    [
        "customer_id",
        "customer_state"
    ]
]

orders = orders[
    [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
]

order_items = order_items[
    [
        "order_id",
        "price",
        "freight_value"
    ]
]

payments = payments[
    [
        "order_id",
        "payment_type",
        "payment_installments",
        "payment_value"
    ]
]

reviews = reviews[
    [
        "order_id",
        "review_score"
    ]
]

# ===================================================
# MERGE DATASETS
# ===================================================

df = orders.merge(customers, on="customer_id", how="left")

df = df.merge(order_items, on="order_id", how="left")

df = df.merge(payments, on="order_id", how="left")

df = df.merge(reviews, on="order_id", how="left")

# ===================================================
# FEATURE ENGINEERING
# ===================================================

# -----------------------------
# DELIVERY DELAY
# -----------------------------

df["delivery_delay_days"] = (
    df["order_delivered_customer_date"]
    - df["order_estimated_delivery_date"]
).dt.days

# negative delays = early delivery
# replace NaN with 0

df["delivery_delay_days"] = df["delivery_delay_days"].fillna(0)

# -----------------------------
# TOTAL ORDER VALUE
# -----------------------------

df["total_order_value"] = (
    df["price"] + df["freight_value"]
)

# ===================================================
# CREATE REFERENCE DATE
# ===================================================

reference_date = df["order_purchase_timestamp"].max()

print("\nREFERENCE DATE:")
print(reference_date)

# ===================================================
# CUSTOMER-LEVEL FEATURES
# ===================================================

customer_features = df.groupby("customer_id").agg(

    # --------------------------------
    # RECENCY
    # --------------------------------

    recency_days=(
        "order_purchase_timestamp",
        lambda x: (reference_date - x.max()).days
    ),

    # --------------------------------
    # FREQUENCY
    # --------------------------------

    frequency=(
        "order_id",
        "nunique"
    ),

    # --------------------------------
    # MONETARY
    # --------------------------------

    monetary_value=(
        "total_order_value",
        "sum"
    ),

    # --------------------------------
    # REVIEW SCORE
    # --------------------------------

    avg_review_score=(
        "review_score",
        "mean"
    ),

    # --------------------------------
    # PAYMENT VALUE
    # --------------------------------

    avg_payment_value=(
        "payment_value",
        "mean"
    ),

    # --------------------------------
    # INSTALLMENTS
    # --------------------------------

    avg_installments=(
        "payment_installments",
        "mean"
    ),

    # --------------------------------
    # DELIVERY DELAY
    # --------------------------------

    avg_delivery_delay=(
        "delivery_delay_days",
        "mean"
    )

).reset_index()

# ===================================================
# CREATE CHURN LABEL
# ===================================================

# churn = no purchase in last 180 days

customer_features["churn"] = customer_features[
    "recency_days"
].apply(lambda x: 1 if x > 180 else 0)

# ===================================================
# BASIC OUTPUT
# ===================================================

print("\nCUSTOMER FEATURE TABLE:")
print(customer_features.head())

print("\nSHAPE:")
print(customer_features.shape)

print("\nCHURN DISTRIBUTION:")
print(customer_features["churn"].value_counts())

# ===================================================
# EXPORT CSV
# ===================================================

customer_features.to_csv(
    "customer_churn_features.csv",
    index=False
)

print("\ncustomer_churn_features.csv exported successfully!")