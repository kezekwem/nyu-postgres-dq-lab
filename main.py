from __future__ import annotations

import json

from src.pipeline import run_pipeline


def main() -> None:
    summary = run_pipeline()
    # Pretty-print a subset so Codespaces users can quickly inspect results.
    safe_summary = summary.copy()
    safe_summary["stakeholder_reply"] = str(summary["stakeholder_reply"].resolve())
    safe_summary["run_log"] = str(summary["run_log"].resolve())
    print("\n=== Pipeline Summary ===")
    print(json.dumps(safe_summary, indent=2, default=str))


if __name__ == "__main__":
    main()
