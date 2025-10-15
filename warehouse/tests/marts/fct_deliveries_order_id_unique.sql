SELECT order_id, COUNT(*) AS cnt
FROM fct_deliveries
GROUP BY order_id
HAVING COUNT(*) <> 1;
