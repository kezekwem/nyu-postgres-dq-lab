CREATE VIEW stg_orders AS
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
    payment_method,
    CAST(NULLIF(trim(subtotal), '') AS REAL) AS subtotal,
    CAST(NULLIF(trim(delivery_fee), '') AS REAL) AS delivery_fee,
    CAST(NULLIF(trim(tip_amount), '') AS REAL) AS tip_amount,
    CAST(NULLIF(trim(distance_km), '') AS REAL) AS distance_km,
    ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_timestamp) AS rn
  FROM orders
),
dedup AS (
  SELECT * FROM base WHERE rn = 1
),
clean AS (
  SELECT
    *,
    CASE
      WHEN status_norm IN ('delivered','canceled','returned') THEN status_norm
      WHEN status_norm IS NULL OR status_norm = '' THEN 'unknown'
      ELSE 'unknown'
    END AS status_final,
    CASE
      WHEN pickup_ts IS NOT NULL AND dropoff_ts IS NOT NULL
        THEN (strftime('%s', dropoff_ts) - strftime('%s', pickup_ts)) / 60.0
      ELSE NULL
    END AS delivery_minutes
  FROM dedup
)
SELECT
  order_id,
  customer_id,
  restaurant_id,
  courier_id,
  order_ts,
  pickup_ts,
  dropoff_ts,
  status_final AS status,
  payment_method,
  subtotal,
  delivery_fee,
  tip_amount,
  distance_km,
  delivery_minutes,
  CASE WHEN status_final = 'delivered' AND delivery_minutes <= 45 THEN 1 ELSE 0 END AS on_time_flag
FROM clean;
