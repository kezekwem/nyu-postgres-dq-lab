"""High level orchestration for the DashDash data quality lab."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

from .config import DATA_DIR, Settings, mask_url
from .data_bootstrap import ensure_sample_csvs, preview_csvs
from .db import EngineFactory, set_search_path_safely, smoke_test
from .reporting import export_views, generate_stakeholder_reply
from .seed import load_tables, verify_row_counts
from .sql_runner import list_sql_files, run_sql_files
from .tests_runner import RUN_LOG_PATH, load_tests, run_tests

logger = logging.getLogger(__name__)


def _print_test_results(prefix: str, results) -> None:
    for result in results:
        if result.severity == "error" and result.failures:
            badge = "❌"
        elif result.failures:
            badge = "🔶"
        else:
            badge = "✅"
        extra = f" → stored in {result.failure_table}" if result.failure_table else ""
        logger.info("%s %s %s: %s failing rows%s", prefix, badge, result.name, result.failures, extra)


def run_pipeline(settings: Settings | None = None) -> Dict[str, object]:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    settings = settings or Settings.from_env()
    factory = EngineFactory(settings)
    logger.info("Using database URL %s", mask_url(settings.database_url))

    smoke_test(factory)
    set_search_path_safely(factory)

    dialect = factory.dialect

    csv_paths = ensure_sample_csvs(DATA_DIR)
    previews = preview_csvs(csv_paths)
    for name, df in previews.items():
        logger.info("CSV %s ready with shape %s", name, df.shape)

    row_counts = load_tables(factory)
    logger.info("Seeded tables: %s", row_counts)
    verified_counts = verify_row_counts(factory)
    logger.info("Row count verification: %s", verified_counts)

    staging_files = list_sql_files("staging", dialect)
    run_sql_files(factory, staging_files)
    logger.info("Created staging views: %s", [f.stem for f in staging_files])

    RUN_LOG_PATH.write_text("", encoding="utf-8")
    staging_tests = load_tests(Path("warehouse/tests/staging.yml"))
    staging_results = run_tests(factory, staging_tests, "staging tests")
    _print_test_results("Staging", staging_results)

    mart_files = list_sql_files("marts", dialect)
    run_sql_files(factory, mart_files)
    logger.info("Created marts: %s", [f.stem for f in mart_files])

    mart_tests = load_tests(Path("warehouse/tests/marts.yml"))
    mart_results = run_tests(factory, mart_tests, "mart tests")
    _print_test_results("Marts", mart_results)

    kpi_files = list_sql_files("kpis", dialect)
    run_sql_files(factory, kpi_files)
    logger.info("Materialized KPI views: %s", [f.stem for f in kpi_files])

    monitoring_files = list_sql_files("monitoring", dialect)
    run_sql_files(factory, monitoring_files)
    logger.info("Materialized monitoring views: %s", [f.stem for f in monitoring_files])

    custom_tests = load_tests(Path("warehouse/tests/custom.yml"))
    custom_results = run_tests(factory, custom_tests, "custom tests")
    _print_test_results("Custom", custom_results)

    reply_path = generate_stakeholder_reply(factory, settings)
    export_counts = export_views(factory)

    summary = {
        "row_counts": row_counts,
        "verified_counts": verified_counts,
        "staging_tests": [r.as_dict() for r in staging_results],
        "mart_tests": [r.as_dict() for r in mart_results],
        "custom_tests": [r.as_dict() for r in custom_results],
        "stakeholder_reply": reply_path,
        "exports": export_counts,
        "run_log": RUN_LOG_PATH,
    }

    logger.info("Stakeholder reply written to %s", reply_path)
    for view, count in export_counts.items():
        logger.info("Exported %s (%s rows)", view, count)
    logger.info("Run log available at %s", RUN_LOG_PATH)

    return summary
