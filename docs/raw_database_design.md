# ShopSphere Raw Database Design

## 1. Raw Tables

| Table | Grain | Primary Key |
|---|---|---|
| raw.customers | One row per customer record | customer_id |
| raw.geolocation | One row per geolocation record | None initially |
| raw.orders | One row per order | order_id |
| raw.order_items | One row per order item | order_id + order_item_id |
| raw.payments | One row per payment record | order_id + payment_sequential |
| raw.order_reviews | One row per review | review_id |
| raw.products | One row per product | product_id |
| raw.sellers | One row per seller | seller_id |
| raw.product_category_translation | One row per category translation | product_category_name |

## 2. Relationships

### Customers → Orders

One customer can have many orders.

`raw.customers.customer_id`
→
`raw.orders.customer_id`

### Orders → Order Items

One order can contain many order items.

`raw.orders.order_id`
→
`raw.order_items.order_id`

### Orders → Payments

One order can have multiple payment records.

`raw.orders.order_id`
→
`raw.payments.order_id`

### Orders → Reviews

An order can have one or more review records.

`raw.orders.order_id`
→
`raw.order_reviews.order_id`

### Products → Order Items

One product can appear in many order items.

`raw.products.product_id`
→
`raw.order_items.product_id`

### Sellers → Order Items

One seller can be associated with many order items.

`raw.sellers.seller_id`
→
`raw.order_items.seller_id`

### Products → Category Translation

Products contain a category name which can be mapped to the
English category translation.

`raw.products.product_category_name`
→
`raw.product_category_translation.product_category_name`

## 3. Design Principles

- Raw tables preserve the source data structure.
- Raw column names are not unnecessarily renamed.
- Source data should remain traceable.
- Primary keys should reflect the actual grain.
- Composite keys are used where a single column does not uniquely identify a record.
- Foreign-key relationships will be validated before being enforced where appropriate.
- Transformations will primarily occur in the staging layer.