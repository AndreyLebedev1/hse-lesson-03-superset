-- raw: исходные CSV без фильтров и агрегаций.
-- analytics: готовый источник для графиков в Superset.
DROP SCHEMA IF EXISTS analytics CASCADE;
DROP SCHEMA IF EXISTS raw CASCADE;
CREATE SCHEMA raw;
CREATE SCHEMA analytics;

CREATE TABLE raw.customers (
    customer_id TEXT PRIMARY KEY,
    customer_unique_id TEXT NOT NULL,
    customer_zip_code_prefix TEXT,
    customer_city TEXT,
    customer_state TEXT
);

CREATE TABLE raw.orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    order_status TEXT NOT NULL,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

CREATE TABLE raw.order_items (
    order_id TEXT NOT NULL,
    order_item_id INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    seller_id TEXT NOT NULL,
    shipping_limit_date TIMESTAMP,
    price NUMERIC(18, 2),
    freight_value NUMERIC(18, 2),
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE raw.products (
    product_id TEXT PRIMARY KEY,
    product_category_name TEXT,
    product_name_lenght NUMERIC,
    product_description_lenght NUMERIC,
    product_photos_qty NUMERIC,
    product_weight_g NUMERIC,
    product_length_cm NUMERIC,
    product_height_cm NUMERIC,
    product_width_cm NUMERIC
);

CREATE TABLE raw.category_translation (
    product_category_name TEXT PRIMARY KEY,
    product_category_name_english TEXT
);

-- Зерно представления: одна товарная позиция заказа.
-- LEFT JOIN сохраняет позицию, даже если у товара нет категории или перевода.
CREATE VIEW analytics.olist_items AS
SELECT
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    i.shipping_limit_date,
    i.price,
    i.freight_value,
    i.price + i.freight_value AS item_total,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_purchase_timestamp::date AS purchase_date,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    p.product_category_name,
    t.product_category_name_english,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
FROM raw.order_items AS i
LEFT JOIN raw.orders AS o ON o.order_id = i.order_id
LEFT JOIN raw.customers AS c ON c.customer_id = o.customer_id
LEFT JOIN raw.products AS p ON p.product_id = i.product_id
LEFT JOIN raw.category_translation AS t
    ON t.product_category_name = p.product_category_name;

GRANT CONNECT ON DATABASE olist TO olist_reader;
GRANT USAGE ON SCHEMA raw, analytics TO olist_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA raw, analytics TO olist_reader;

