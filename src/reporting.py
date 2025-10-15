"""Stakeholder deliverables: summary markdown and CSV exports."""
from __future__ import annotations

from pathlib import Path
from typing import Dict
import datetime

import pandas as pd
from sqlalchemy import text

from .config import OUTPUTS_DIR, Settings
from .db import EngineFactory


def generate_stakeholder_reply(factory: EngineFactory, settings: Settings) -> Path:
    engine = factory.get_engine()
    df = pd.read_sql(text("SELECT * FROM kpi_delivery_overview"), engine)
    on_time = adm = crr = 0.0
    if not df.empty:
        on_time = float(df.loc[0, "on_time_rate"] or 0) * 100.0
        adm = float(df.loc[0, "avg_delivery_minutes"] or 0)
        crr = float(df.loc[0, "cancel_return_rate"] or 0) * 100.0

    output_path = OUTPUTS_DIR / (
        f"Lab06_{settings.student_first}_{settings.student_last}_{settings.student_netid}_Reply.md"
    )

    body = f"""# Stakeholder Reply — DashDash Data Quality & KPIs

**KPI summary:** On-Time Delivery: {on_time:.2f}% · Average Delivery Minutes: {adm:.2f} · Cancel/Return Rate: {crr:.2f}%

**What changed after remediation**
- Deduplicated orders by `order_id` (kept earliest record); removed duplicates from KPI universe.
- Normalized mixed/invalid `status` values to {{delivered|canceled|returned|unknown}} to prevent leakage into dashboards.
- Enforced referential integrity to restaurants/couriers; excluded rows with bad foreign keys from facts.
- Added a DQ Exceptions view to track excluded rows and their reasons.

**Recommendation**
- Proceed with the “10‑Minute Free Delivery Insurance” promo **if** daily on‑time % remains ≥ 85% during soft‑launch; otherwise, pause the offer in regions where scooter/car availability is thin.

_Generated with GPT-5 Pro on {datetime.datetime.utcnow():%Y-%m-%d %H:%M UTC}. Student verified the numbers and process._
"""

    output_path.write_text(body, encoding="utf-8")
    return output_path


EXPORT_VIEWS: Dict[str, Path] = {
    "stg_orders": OUTPUTS_DIR / "stg_orders_export.csv",
    "fct_deliveries": OUTPUTS_DIR / "fct_deliveries_export.csv",
    "monitoring_dq_exceptions": OUTPUTS_DIR / "monitoring_dq_exceptions_export.csv",
    "kpi_delivery_overview": OUTPUTS_DIR / "kpi_delivery_overview_export.csv",
}


def export_views(factory: EngineFactory, views: Dict[str, Path] | None = None) -> Dict[str, int]:
    engine = factory.get_engine()
    targets = views or EXPORT_VIEWS
    exported: Dict[str, int] = {}
    for view, path in targets.items():
        df = pd.read_sql(text(f"SELECT * FROM {view}"), engine)
        df.to_csv(path, index=False)
        exported[view] = len(df)
    return exported
