CREATE OR REPLACE VIEW stg_couriers AS
SELECT
  courier_id,
  courier_name,
  lower(vehicle_type) AS vehicle_type,
  active_from,
  active_to,
  region
FROM couriers;
