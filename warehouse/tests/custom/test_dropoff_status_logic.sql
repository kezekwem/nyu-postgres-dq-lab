SELECT *
FROM stg_orders
WHERE (status IN ('canceled','returned') AND dropoff_ts IS NOT NULL)
   OR (status = 'delivered' AND dropoff_ts IS NULL);
