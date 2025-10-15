SELECT f.*
FROM fct_deliveries f
LEFT JOIN dim_restaurant d ON f.restaurant_id = d.restaurant_id
WHERE d.restaurant_id IS NULL;
