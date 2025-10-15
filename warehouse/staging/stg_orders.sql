CREATE OR REPLACE VIEW stg_orders AS
WITH base AS (
  SELECT
    order_id,
    customer_id,
    restaurant_id,
    courier_id,
    NULLIF(order_timestamp,'')::timestamp    AS order_ts,
    NULLIF(pickup_timestamp,'')::timestamp   AS pickup_ts,
    NULLIF(dropoff_timestamp,'')::timestamp  AS dropoff_ts,
    lower(trim(NULLIF(status,'')))           AS status_norm,
    payment_method,
    NULLIF(subtotal,'')::numeric(10,2)       AS subtotal,
    NULLIF(delivery_fee,'')::numeric(10,2)   AS delivery_fee,
    NULLIF(tip_amount,'')::numeric(10,2)     AS tip_amount,
    NULLIF(distance_km,'')::numeric(6,2)     AS distance_km,
    row_number() OVER (PARTITION BY order_id ORDER BY order_timestamp) AS rn
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
      WHEN status_norm IS NULL THEN 'unknown'
      ELSE 'unknown'
    END AS status_final,
    CASE
      WHEN pickup_ts IS NOT NULL AND dropoff_ts IS NOT NULL
        THEN EXTRACT(epoch FROM (dropoff_ts - pickup_ts))/60.0
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
  CASE WHEN status_final = 'delivered' AND delivery_minutes <= 45 THEN TRUE ELSE FALSE END AS on_time_flag
FROM clean;
