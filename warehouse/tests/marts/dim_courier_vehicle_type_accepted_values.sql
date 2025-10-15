SELECT *
FROM dim_courier
WHERE vehicle_type NOT IN ('bike','scooter','car') OR vehicle_type IS NULL;
