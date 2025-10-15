"""Helpers for executing SQL files in dependency order."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy import text

from .config import WAREHOUSE_DIR
from .db import EngineFactory


def _parse_sql_filename(path: Path) -> Tuple[str, Optional[str]]:
    """Return logical name and optional dialect tag for a SQL file."""

    parts = path.name.split(".")
    if len(parts) >= 3:
        dialect = parts[-2]
        base = ".".join(parts[:-2])
        if dialect in {"sqlite", "postgres", "postgresql"}:
            normalized = "postgresql" if dialect in {"postgres", "postgresql"} else dialect
            return base, normalized
    return path.stem, None


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


def list_sql_files(relative_dir: str, dialect: str) -> List[Path]:
    target = WAREHOUSE_DIR / relative_dir
    choices: Dict[str, Dict[Optional[str], Path]] = {}
    for path in target.glob("*.sql"):
        base, tag = _parse_sql_filename(path)
        bucket = choices.setdefault(base, {})
        bucket[tag] = path

    normalized_dialect = "postgresql" if dialect in {"postgres", "postgresql"} else dialect
    selected: List[Path] = []
    for base in sorted(choices):
        bucket = choices[base]
        if normalized_dialect in bucket:
            selected.append(bucket[normalized_dialect])
        elif None in bucket:
            selected.append(bucket[None])
    return selected
