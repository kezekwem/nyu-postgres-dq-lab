CREATE VIEW kpi_delivery_overview AS
WITH d AS (SELECT * FROM fct_deliveries)
SELECT
  AVG(CASE WHEN on_time_flag = 1 THEN 1.0 ELSE 0.0 END) AS on_time_rate,
  AVG(delivery_minutes) AS avg_delivery_minutes,
  (
    SELECT
      CAST(SUM(CASE WHEN status IN ('canceled','returned') THEN 1 ELSE 0 END) AS REAL)
      / NULLIF(COUNT(*), 0)
    FROM stg_orders
  ) AS cancel_return_rate;
