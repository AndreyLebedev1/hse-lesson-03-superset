-- 1. Сколько строк попало в каждую исходную таблицу?
SELECT 'customers' AS table_name, COUNT(*) AS rows_count FROM raw.customers
UNION ALL
SELECT 'orders', COUNT(*) FROM raw.orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM raw.order_items
UNION ALL
SELECT 'products', COUNT(*) FROM raw.products
UNION ALL
SELECT 'category_translation', COUNT(*) FROM raw.category_translation;

-- 2. Какой период покрывают заказы?
SELECT
    MIN(order_purchase_timestamp) AS first_order,
    MAX(order_purchase_timestamp) AS last_order
FROM raw.orders;

-- 3. Месячная динамика для первого графика Superset.
SELECT
    DATE_TRUNC('month', order_purchase_timestamp) AS month,
    COUNT(DISTINCT order_id) AS orders,
    SUM(price) AS revenue
FROM analytics.olist_items
GROUP BY 1
ORDER BY 1;

