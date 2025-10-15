CREATE VIEW monitoring_dq_exceptions AS
WITH base AS (
  SELECT
    order_id,
    customer_id,
    restaurant_id,
    courier_id,
    CASE WHEN trim(order_timestamp) = '' THEN NULL ELSE datetime(order_timestamp) END AS order_ts,
    CASE WHEN trim(pickup_timestamp) = '' THEN NULL ELSE datetime(pickup_timestamp) END AS pickup_ts,
    CASE WHEN trim(dropoff_timestamp) = '' THEN NULL ELSE datetime(dropoff_timestamp) END AS dropoff_ts,
    lower(trim(COALESCE(status, ''))) AS status_norm,
    ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_timestamp) AS rn
  FROM orders
),
dupes AS (
  SELECT order_id, 'duplicate_order' AS reason FROM base WHERE rn > 1
),
bad_rest_fk AS (
  SELECT o.order_id, 'bad_fk_restaurant' AS reason
  FROM orders o
  LEFT JOIN stg_restaurants r ON o.restaurant_id = r.restaurant_id
  WHERE r.restaurant_id IS NULL
),
bad_cour_fk AS (
  SELECT o.order_id, 'bad_fk_courier' AS reason
  FROM orders o
  LEFT JOIN stg_couriers c ON o.courier_id = c.courier_id
  WHERE o.courier_id IS NOT NULL AND c.courier_id IS NULL
),
unknown_status AS (
  SELECT order_id, 'status_unknown' AS reason
  FROM base
  WHERE status_norm = '' OR status_norm NOT IN ('delivered','canceled','returned')
)
SELECT DISTINCT order_id, reason
FROM (
  SELECT * FROM dupes
  UNION ALL SELECT * FROM bad_rest_fk
  UNION ALL SELECT * FROM bad_cour_fk
  UNION ALL SELECT * FROM unknown_status
) u
ORDER BY order_id, reason;
