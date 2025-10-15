"""Utilities for preparing lab CSV inputs."""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Dict

import pandas as pd

from .config import DATA_DIR

SAMPLE_CSV_CONTENT: Dict[str, str] = {
    "restaurants.csv": dedent(
        """restaurant_id,restaurant_name,cuisine
1,Pasta Palace,Italian
2,Sushi Central,Japanese
3,Taco Tower,Mexican
4,Curry Corner,Indian
5,Burger Barn,American"""
    ).strip()
    + "\n",
    "couriers.csv": dedent(
        """courier_id,courier_name,vehicle_type,active_from,active_to,region
10,Alex Rider,Bike,2024-01-01,,north
11,Brooke Sky,Car,2024-03-15,,south
12,Casey Night,Scooter,2024-05-10,,west
13,Dee Lane,Truck,2024-02-01,,east"""
    ).strip()
    + "\n",
    "customers.csv": dedent(
        """customer_id,customer_name,email,city
101,Alice Lee,alice@example.com,New York
102,Bob Kim,bob@example.com,Boston
103,Carla Diaz,carla@example.com,Chicago
104,Diego Park,diego@example.com,Seattle
105,Eve Sun,eve@example.com,Austin"""
    ).strip()
    + "\n",
    "orders.csv": dedent(
        """order_id,customer_id,restaurant_id,courier_id,order_timestamp,pickup_timestamp,dropoff_timestamp,status,payment_method,subtotal,delivery_fee,tip_amount,distance_km
2001,101,1,10.0,2025-10-01 12:00:00,2025-10-01 12:10:00,2025-10-01 12:35:00,Delivered,card,45.5,4.99,6.0,3.1
2002,102,2,11.0,2025-10-01 12:05:00,2025-10-01 12:20:00,2025-10-01 13:20:00,Delivered,card,28.0,3.99,5.0,7.0
2002,102,2,11.0,2025-10-01 12:06:00,2025-10-01 12:21:00,2025-10-01 13:21:00,DELIVERED,card,28.0,3.99,5.0,7.0
2003,103,3,12.0,2025-10-02 18:40:00,2025-10-02 18:50:00,2025-10-02 19:05:00,Canceled,card,18.75,4.25,0.0,2.2
2004,104,4,13.0,2025-10-02 19:00:00,2025-10-02 19:12:00,2025-10-02 19:36:00,Returned,cash,26.0,4.99,0.0,5.8
2005,105,5,,2025-10-03 11:00:00,2025-10-03 11:15:00,2025-10-03 11:37:00,delivered,card,19.5,2.99,2.0,1.4
2006,101,999,12.0,2025-10-03 12:10:00,2025-10-03 12:25:00,2025-10-03 12:55:00,,card,30.0,3.99,4.5,6.2
2007,102,2,11.0,2025-10-03 20:00:00,2025-10-03 20:15:00,2025-10-03 20:58:00,Unknown,cash,15.0,3.5,0.0,4.5
2008,103,3,12.0,2025-10-04 08:30:00,,,Delivered,card,12.0,3.0,2.0,1.0"""
    ).strip()
    + "\n",
}


def ensure_sample_csvs(data_dir: Path | None = None) -> Dict[str, Path]:
    """Create the lab CSVs if they are missing and return their paths."""

    target_dir = data_dir or DATA_DIR
    target_dir.mkdir(exist_ok=True)

    csv_paths: Dict[str, Path] = {}
    for name, contents in SAMPLE_CSV_CONTENT.items():
        dest = target_dir / name
        if not dest.exists():
            dest.write_text(contents, encoding="utf-8")
        csv_paths[name] = dest
    return csv_paths


def preview_csvs(csv_paths: Dict[str, Path]) -> Dict[str, pd.DataFrame]:
    """Return a quick pandas preview for each CSV (mirrors notebook preview)."""

    previews: Dict[str, pd.DataFrame] = {}
    for name, path in csv_paths.items():
        try:
            previews[name] = pd.read_csv(path)
        except Exception as exc:  # pragma: no cover - diagnostic only
            raise RuntimeError(f"Unable to read CSV {path}") from exc
    return previews
