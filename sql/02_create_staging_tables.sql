-- ============================================================
-- ShopSphere Analytics
-- Step 10.1 — Create Staging Tables
-- ============================================================


-- 1. Customers
CREATE TABLE IF NOT EXISTS staging.customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix INTEGER,
    customer_city VARCHAR(100),
    customer_state VARCHAR(10)
);


-- 2. Geolocation
CREATE TABLE IF NOT EXISTS staging.geolocation (
    geolocation_zip_code_prefix INTEGER,
    geolocation_lat NUMERIC(10,6),
    geolocation_lng NUMERIC(10,6),
    geolocation_city VARCHAR(100),
    geolocation_state VARCHAR(10)
);


-- 3. Orders
CREATE TABLE IF NOT EXISTS staging.orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    order_status VARCHAR(30),
    order_purchase_timestamp TIMESTAMP NOT NULL,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);


-- 4. Order Items
CREATE TABLE IF NOT EXISTS staging.order_items (
    order_id VARCHAR(50) NOT NULL,
    order_item_id INTEGER NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    seller_id VARCHAR(50) NOT NULL,
    shipping_limit_date TIMESTAMP,
    price NUMERIC(12,2) CHECK (price >= 0),
    freight_value NUMERIC(12,2) CHECK (freight_value >= 0),

    PRIMARY KEY (order_id, order_item_id)
);


-- 5. Payments
CREATE TABLE IF NOT EXISTS staging.payments (
    order_id VARCHAR(50) NOT NULL,
    payment_sequential INTEGER NOT NULL,
    payment_type VARCHAR(30),
    payment_installments INTEGER CHECK (payment_installments >= 1),
    payment_value NUMERIC(12,2) CHECK (payment_value >= 0),

    PRIMARY KEY (order_id, payment_sequential)
);


-- 6. Order Reviews
CREATE TABLE IF NOT EXISTS staging.order_reviews (
    review_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    review_score INTEGER CHECK (review_score BETWEEN 1 AND 5),
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);


-- 7. Products
CREATE TABLE IF NOT EXISTS staging.products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_lenght INTEGER CHECK (product_name_lenght >= 0),
    product_description_lenght INTEGER CHECK (product_description_lenght >= 0),
    product_photos_qty INTEGER CHECK (product_photos_qty >= 0),
    product_weight_g NUMERIC(12,2) CHECK (product_weight_g >= 0),
    product_length_cm NUMERIC(10,2) CHECK (product_length_cm >= 0),
    product_height_cm NUMERIC(10,2) CHECK (product_height_cm >= 0),
    product_width_cm NUMERIC(10,2) CHECK (product_width_cm >= 0)
);


-- 8. Sellers
CREATE TABLE IF NOT EXISTS staging.sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix INTEGER,
    seller_city VARCHAR(100),
    seller_state VARCHAR(10)
);


-- 9. Product Category Translation
CREATE TABLE IF NOT EXISTS staging.product_category_translation (
    product_category_name VARCHAR(100) PRIMARY KEY,
    product_category_name_english VARCHAR(100)
);