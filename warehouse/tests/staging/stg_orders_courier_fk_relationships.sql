SELECT o.*
FROM stg_orders o
LEFT JOIN stg_couriers c ON o.courier_id = c.courier_id
WHERE o.courier_id IS NOT NULL AND c.courier_id IS NULL;
