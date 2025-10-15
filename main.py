from __future__ import annotations

import json

from src.config import Settings, mask_url
from src.pipeline import run_pipeline


def choose_settings() -> Settings:
    settings = Settings.from_env()
    try:
        choice = input("Run pipeline against PostgreSQL? [Y/n]: ").strip().lower()
    except EOFError:
        choice = ""
    if choice in {"n", "no"}:
        settings = settings.for_sqlite()
        print("Using SQLite backend at", settings.database_url)
    else:
        print("Using PostgreSQL backend at", mask_url(settings.database_url))
    return settings


def main() -> None:
    settings = choose_settings()
    summary = run_pipeline(settings=settings)
    # Pretty-print a subset so Codespaces users can quickly inspect results.
    safe_summary = summary.copy()
    safe_summary["stakeholder_reply"] = str(summary["stakeholder_reply"].resolve())
    safe_summary["run_log"] = str(summary["run_log"].resolve())
    print("\n=== Pipeline Summary ===")
    print(json.dumps(safe_summary, indent=2, default=str))


if __name__ == "__main__":
    main()
