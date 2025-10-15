CREATE OR REPLACE VIEW fct_deliveries AS
SELECT *
FROM stg_orders o
WHERE o.status = 'delivered'
  AND o.restaurant_id IN (SELECT restaurant_id FROM stg_restaurants)
  AND (o.courier_id IS NULL OR o.courier_id IN (SELECT courier_id FROM stg_couriers));
