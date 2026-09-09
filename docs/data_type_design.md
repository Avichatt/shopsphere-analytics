# ShopSphere PostgreSQL Data Type Design

## raw.customers

| Column | PostgreSQL Type | Constraint |
|---|---|---|
| customer_id | VARCHAR(50) | PRIMARY KEY |
| customer_unique_id | VARCHAR(50) | NOT NULL |
| customer_zip_code_prefix | INTEGER | |
| customer_city | VARCHAR(100) | |
| customer_state | VARCHAR(10) | |

## raw.geolocation

| Column | PostgreSQL Type | Constraint |
|---|---|---|
| geolocation_zip_code_prefix | INTEGER | |
| geolocation_lat | NUMERIC(10,6) | |
| geolocation_lng | NUMERIC(10,6) | |
| geolocation_city | VARCHAR(100) | |
| geolocation_state | VARCHAR(10) | |

## raw.orders

| Column | PostgreSQL Type | Constraint |
|---|---|---|
| order_id | VARCHAR(50) | PRIMARY KEY |
| customer_id | VARCHAR(50) | NOT NULL |
| order_status | VARCHAR(30) | |
| order_purchase_timestamp | TIMESTAMP | NOT NULL |
| order_approved_at | TIMESTAMP | |
| order_delivered_carrier_date | TIMESTAMP | |
| order_delivered_customer_date | TIMESTAMP | |
| order_estimated_delivery_date | TIMESTAMP | |

## raw.order_items

| Column | PostgreSQL Type | Constraint |
|---|---|---|
| order_id | VARCHAR(50) | NOT NULL |
| order_item_id | INTEGER | NOT NULL |
| product_id | VARCHAR(50) | NOT NULL |
| seller_id | VARCHAR(50) | NOT NULL |
| shipping_limit_date | TIMESTAMP | |
| price | NUMERIC(12,2) | CHECK >= 0 |
| freight_value | NUMERIC(12,2) | CHECK >= 0 |

Primary Key: `(order_id, order_item_id)`

## raw.payments

| Column | PostgreSQL Type | Constraint |
|---|---|---|
| order_id | VARCHAR(50) | NOT NULL |
| payment_sequential | INTEGER | NOT NULL |
| payment_type | VARCHAR(30) | |
| payment_installments | INTEGER | CHECK >= 1 |
| payment_value | NUMERIC(12,2) | CHECK >= 0 |

Primary Key: `(order_id, payment_sequential)`

## raw.order_reviews

| Column | PostgreSQL Type | Constraint |
|---|---|---|
| review_id | VARCHAR(50) | PRIMARY KEY |
| order_id | VARCHAR(50) | NOT NULL |
| review_score | INTEGER | CHECK 1-5 |
| review_comment_title | TEXT | |
| review_comment_message | TEXT | |
| review_creation_date | TIMESTAMP | |
| review_answer_timestamp | TIMESTAMP | |

## raw.products

| Column | PostgreSQL Type | Constraint |
|---|---|---|
| product_id | VARCHAR(50) | PRIMARY KEY |
| product_category_name | VARCHAR(100) | |
| product_name_lenght | INTEGER | CHECK >= 0 |
| product_description_lenght | INTEGER | CHECK >= 0 |
| product_photos_qty | INTEGER | CHECK >= 0 |
| product_weight_g | NUMERIC(12,2) | CHECK >= 0 |
| product_length_cm | NUMERIC(10,2) | CHECK >= 0 |
| product_height_cm | NUMERIC(10,2) | CHECK >= 0 |
| product_width_cm | NUMERIC(10,2) | CHECK >= 0 |

## raw.sellers

| Column | PostgreSQL Type | Constraint |
|---|---|---|
| seller_id | VARCHAR(50) | PRIMARY KEY |
| seller_zip_code_prefix | INTEGER | |
| seller_city | VARCHAR(100) | |
| seller_state | VARCHAR(10) | |

## raw.product_category_translation

| Column | PostgreSQL Type | Constraint |
|---|---|---|
| product_category_name | VARCHAR(100) | PRIMARY KEY |
| product_category_name_english | VARCHAR(100) | |