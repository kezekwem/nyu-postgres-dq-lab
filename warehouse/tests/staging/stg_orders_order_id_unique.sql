SELECT order_id, COUNT(*) AS cnt
FROM stg_orders
GROUP BY order_id
HAVING COUNT(*) <> 1;
