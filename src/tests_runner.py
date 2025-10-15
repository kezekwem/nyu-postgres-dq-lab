"""Execute SQL-based data quality tests defined in YAML."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
import json
import datetime

import pandas as pd
from sqlalchemy import text
import yaml

from .config import OUTPUTS_DIR, WAREHOUSE_DIR
from .db import EngineFactory

RUN_LOG_PATH = OUTPUTS_DIR / "RUN_LOG.txt"


@dataclass
class TestCase:
    name: str
    severity: str
    sql_file: Path
    store_failures: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "TestCase":
        sql_path = data["sql"]
        path = (WAREHOUSE_DIR / sql_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Test SQL not found: {path}")
        return cls(
            name=data["name"],
            severity=data.get("severity", "error"),
            sql_file=path,
            store_failures=data.get("store_failures", True),
        )


@dataclass
class TestResult:
    name: str
    severity: str
    failures: int
    failure_table: str | None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "severity": self.severity,
            "failures": self.failures,
            "failure_table": self.failure_table,
        }


def load_tests(config_file: Path) -> List[TestCase]:
    config = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    items = config.get("tests", [])
    return [TestCase.from_dict(item) for item in items]


def run_tests(factory: EngineFactory, tests: Iterable[TestCase], group_name: str) -> List[TestResult]:
    RUN_LOG_PATH.touch(exist_ok=True)
    results: List[TestResult] = []
    engine = factory.get_engine()
    for test in tests:
        sql_text = test.sql_file.read_text(encoding="utf-8")
        df = pd.read_sql(text(sql_text), engine)
        failure_table = f"dq_failures__{test.name}"
        with factory.connect() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{failure_table}"'))
            conn.commit()
        if test.store_failures and not df.empty:
            df.to_sql(failure_table, con=engine, if_exists="replace", index=False)
        result = TestResult(
            name=test.name,
            severity=test.severity,
            failures=len(df),
            failure_table=failure_table if (test.store_failures and not df.empty) else None,
        )
        results.append(result)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with RUN_LOG_PATH.open("a", encoding="utf-8") as log:
        log.write(f"\n[{timestamp}] {group_name.upper()}\n")
        for result in results:
            log.write(json.dumps(result.as_dict()) + "\n")
    return results
