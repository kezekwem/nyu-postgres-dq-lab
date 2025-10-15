SELECT *
FROM stg_orders
WHERE NOT (delivery_minutes IS NULL OR delivery_minutes >= 0);
