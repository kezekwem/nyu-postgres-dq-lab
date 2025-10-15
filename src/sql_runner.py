"""Helpers for executing SQL files in dependency order."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from sqlalchemy import text

from .config import WAREHOUSE_DIR
from .db import EngineFactory


def load_sql(path: Path) -> str:
    sql = path.read_text(encoding="utf-8")
    return sql.strip() + (";" if not sql.strip().endswith(";") else "")


def run_sql_files(factory: EngineFactory, files: Iterable[Path]) -> List[Path]:
    executed: List[Path] = []
    with factory.connect() as conn:
        for file in files:
            sql_text = file.read_text(encoding="utf-8")
            conn.execute(text(sql_text))
            executed.append(file)
        conn.commit()
    return executed


def list_sql_files(relative_dir: str) -> List[Path]:
    target = WAREHOUSE_DIR / relative_dir
    return sorted(target.glob("*.sql"))
