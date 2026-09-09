# ShopSphere Data Quality Report

## 1. Overview

This document records data-quality observations
identified during the initial profiling of the source datasets.

---

## 2. Missing Values

| Dataset | Column | Missing Count | Missing % | Severity | Action |
|---|---|---:|---:|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD |

---

## 3. Duplicate Records

| Dataset | Duplicate Count | Expected? | Action |
|---|---:|---|---|
| TBD | TBD | TBD | TBD |

---

## 4. Data Types

| Dataset | Column | Current Type | Expected Type | Action |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD |

---

## 5. Potential Outliers

| Dataset | Column | Observation | Investigation |
|---|---|---|---|
| TBD | TBD | TBD | TBD |

---

## 6. Business Rules

| Rule | Dataset | Column(s) | Status |
|---|---|---|---|
| Order ID should identify an order | orders | order_id | TBD |
| Customer ID should exist for valid orders | orders | customer_id | TBD |
| Product price should not be negative | products | price | TBD |
| Quantity should be positive | order_items | quantity | TBD |

---

## 7. Relationships

| Parent Table | Parent Key | Child Table | Child Key | Expected Relationship |
|---|---|---|---|---|
| customers | customer_id | orders | customer_id | 1-to-many |
| orders | order_id | order_items | order_id | 1-to-many |
| products | product_id | order_items | product_id | 1-to-many |
| orders | order_id | payments | order_id | 1-to-many |