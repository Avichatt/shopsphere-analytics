CREATE TABLE IF NOT EXISTS analytics.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix INTEGER,
    customer_city VARCHAR(100),
    customer_state VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS analytics.dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_category_name VARCHAR(100),
    product_category_name_english VARCHAR(100),
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g NUMERIC(12,2),
    product_length_cm NUMERIC(10,2),
    product_height_cm NUMERIC(10,2),
    product_width_cm NUMERIC(10,2)
);

CREATE TABLE IF NOT EXISTS analytics.dim_seller (
    seller_key SERIAL PRIMARY KEY,
    seller_id VARCHAR(50) NOT NULL UNIQUE,
    seller_zip_code_prefix INTEGER,
    seller_city VARCHAR(100),
    seller_state VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS analytics.dim_order (
    order_key SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL UNIQUE,
    customer_id VARCHAR(50) NOT NULL,
    order_status VARCHAR(30),
    order_purchase_timestamp TIMESTAMP NOT NULL,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

INSERT INTO analytics.dim_date (
    date_key,
    full_date,
    year,
    quarter,
    month,
    month_name,
    week_of_year,
    day_of_month,
    day_of_week,
    day_name,
    is_weekend
)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER AS date_key,
    d::DATE AS full_date,
    EXTRACT(YEAR FROM d)::INTEGER AS year,
    EXTRACT(QUARTER FROM d)::INTEGER AS quarter,
    EXTRACT(MONTH FROM d)::INTEGER AS month,
    TO_CHAR(d, 'Month') AS month_name,
    EXTRACT(WEEK FROM d)::INTEGER AS week_of_year,
    EXTRACT(DAY FROM d)::INTEGER AS day_of_month,
    EXTRACT(ISODOW FROM d)::INTEGER AS day_of_week,
    TO_CHAR(d, 'Day') AS day_name,
    CASE
        WHEN EXTRACT(ISODOW FROM d) IN (6, 7)
        THEN TRUE
        ELSE FALSE
    END AS is_weekend
FROM generate_series(
    (SELECT MIN(order_purchase_timestamp)::DATE
     FROM staging.orders),
    (SELECT MAX(order_purchase_timestamp)::DATE
     FROM staging.orders),
    INTERVAL '1 day'
) AS dates(d);

CREATE TABLE IF NOT EXISTS analytics.fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,

    order_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    seller_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,

    order_id VARCHAR(50) NOT NULL,
    order_item_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price NUMERIC(12,2) NOT NULL,
    freight_value NUMERIC(12,2) NOT NULL,
    sales_amount NUMERIC(12,2) NOT NULL,

    CONSTRAINT uq_fact_sales_order_item
        UNIQUE (order_id, order_item_id)
);

CREATE TABLE IF NOT EXISTS analytics.fact_reviews (
    review_key BIGSERIAL PRIMARY KEY,

    order_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,

    review_id VARCHAR(50) NOT NULL UNIQUE,
    order_id VARCHAR(50) NOT NULL,

    review_score INTEGER NOT NULL
        CHECK (review_score BETWEEN 1 AND 5),

    review_comment_title TEXT,
    review_comment_message TEXT,

    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);