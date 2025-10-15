SELECT *
FROM stg_orders
WHERE status NOT IN ('delivered','canceled','returned','unknown')
   OR status IS NULL;
