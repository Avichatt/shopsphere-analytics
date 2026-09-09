Document:

Fact table: fact_sales
Grain: one row per order item
Measures: sales_amount, quantity, discount, etc.
Foreign Keys: Connects to dimensions

Dimensions: 
dim_customer → customer details (name, city, state)
dim_product → product attributes (category, brand)
dim_seller → seller info (location, rating)
dim_order → order metadata (status, timestamps)
dim_date → calendar attributes (day, month, year, holiday flag)

A simple diagram similar to the one above
                dim_customer
                     |
dim_product — fact_sales — dim_seller
                     |
                dim_order
                     |
                 dim_date

A short explanation of why we're using a star schema:

The star schema keeps your warehouse design clean and efficient. fact_sales captures the events (order items), while dimensions provide the context (who, what, when, where).