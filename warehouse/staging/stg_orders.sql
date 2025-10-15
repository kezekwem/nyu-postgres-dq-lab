CREATE OR REPLACE VIEW stg_orders AS
WITH base AS (
  SELECT
    order_id,
    customer_id,
    restaurant_id,
    courier_id,
    NULLIF(BTRIM(order_timestamp::text),'')::timestamp    AS order_ts,
    NULLIF(BTRIM(pickup_timestamp::text),'')::timestamp   AS pickup_ts,
    NULLIF(BTRIM(dropoff_timestamp::text),'')::timestamp  AS dropoff_ts,
    lower(NULLIF(BTRIM(status::text),''))                 AS status_norm,
    payment_method,
    NULLIF(BTRIM(subtotal::text),'')::numeric(10,2)       AS subtotal,
    NULLIF(BTRIM(delivery_fee::text),'')::numeric(10,2)   AS delivery_fee,
    NULLIF(BTRIM(tip_amount::text),'')::numeric(10,2)     AS tip_amount,
    NULLIF(BTRIM(distance_km::text),'')::numeric(6,2)     AS distance_km,
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
