SELECT o.*
FROM stg_orders o
LEFT JOIN stg_restaurants r ON o.restaurant_id = r.restaurant_id
WHERE r.restaurant_id IS NULL;
