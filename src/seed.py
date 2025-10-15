"""Load CSV data into the Postgres warehouse schema."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
from sqlalchemy import text

from .config import DATA_DIR
from .db import EngineFactory

TABLE_FILES = {
    "restaurants": DATA_DIR / "restaurants.csv",
    "couriers": DATA_DIR / "couriers.csv",
    "customers": DATA_DIR / "customers.csv",
    "orders": DATA_DIR / "orders.csv",
}


DROP_VIEWS_POSTGRES = [
    "DROP VIEW IF EXISTS stg_orders, stg_restaurants, stg_couriers, stg_customers CASCADE;",
    "DROP VIEW IF EXISTS fct_deliveries, dim_restaurant, dim_courier, dim_customer, kpi_delivery_overview, monitoring_dq_exceptions CASCADE;",
]

DROP_VIEWS_SQLITE = [
    "DROP VIEW IF EXISTS stg_orders;",
    "DROP VIEW IF EXISTS stg_restaurants;",
    "DROP VIEW IF EXISTS stg_couriers;",
    "DROP VIEW IF EXISTS stg_customers;",
    "DROP VIEW IF EXISTS fct_deliveries;",
    "DROP VIEW IF EXISTS dim_restaurant;",
    "DROP VIEW IF EXISTS dim_courier;",
    "DROP VIEW IF EXISTS dim_customer;",
    "DROP VIEW IF EXISTS kpi_delivery_overview;",
    "DROP VIEW IF EXISTS monitoring_dq_exceptions;",
]


def load_tables(factory: EngineFactory, table_files: Dict[str, Path] | None = None) -> Dict[str, int]:
    """Load CSVs into PostgreSQL using pandas.to_sql (similar to the notebook)."""

    files = table_files or TABLE_FILES
    engine = factory.get_engine()

    drop_statements = DROP_VIEWS_SQLITE if factory.dialect == "sqlite" else DROP_VIEWS_POSTGRES

    with factory.connect() as conn:
        for statement in drop_statements:
            conn.execute(text(statement))
        conn.commit()

    row_counts: Dict[str, int] = {}
    for table, csv_path in files.items():
        df = pd.read_csv(csv_path)
        df.to_sql(table, con=engine, if_exists="replace", index=False)
        row_counts[table] = len(df)
    return row_counts


def verify_row_counts(factory: EngineFactory, tables: Dict[str, Path] | None = None) -> Dict[str, int]:
    files = tables or TABLE_FILES
    counts: Dict[str, int] = {}
    with factory.connect() as conn:
        for table in files:
            counts[table] = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
    return counts
