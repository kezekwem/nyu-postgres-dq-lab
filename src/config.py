"""Configuration helpers for the DashDash data warehouse lab."""
from __future__ import annotations

from dataclasses import dataclass, replace
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url

# Load environment variables as early as possible so every module picks them up.
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
WAREHOUSE_DIR = BASE_DIR / "warehouse"

DATA_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)


@dataclass(frozen=True)
class Settings:
    """Runtime configuration derived from environment variables."""

    database_url: str
    student_first: str
    student_last: str
    student_netid: str

    @classmethod
    def from_env(cls) -> "Settings":
        pg_host = os.getenv("PGHOST", "YOUR_HOST")
        pg_port = os.getenv("PGPORT", "5432")
        pg_db = os.getenv("PGDATABASE", "YOUR_DBNAME")
        pg_user = os.getenv("PGUSER", "YOUR_USERNAME")
        pg_password = os.getenv("PGPASSWORD", "YOUR_PASSWORD")
        pg_ssl = os.getenv("PGSSL", "require")

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            database_url = (
                f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}?sslmode={pg_ssl}"
            )

        return cls(
            database_url=database_url,
            student_first=os.getenv("STUDENT_FIRST", "First"),
            student_last=os.getenv("STUDENT_LAST", "Last"),
            student_netid=os.getenv("STUDENT_NETID", "netid1234"),
        )

    @property
    def dialect(self) -> str:
        """Return the SQLAlchemy backend name for the configured database URL."""

        return make_url(self.database_url).get_backend_name()

    def with_database_url(self, url: str) -> "Settings":
        """Return a copy of the settings pointing to a different database."""

        return replace(self, database_url=url)

    def for_sqlite(self, path: Path | None = None) -> "Settings":
        """Return settings configured for a SQLite database file."""

        sqlite_url = os.getenv("SQLITE_URL")
        if sqlite_url:
            return self.with_database_url(sqlite_url)

        if path is None:
            env_path = os.getenv("SQLITE_PATH")
            if env_path:
                path = Path(env_path)
            else:
                path = DATA_DIR / "lab.sqlite"

        resolved = Path(path).resolve()
        resolved.parent.mkdir(parents=True, exist_ok=True)
        return self.with_database_url(f"sqlite:///{resolved}")


def mask_url(url: str) -> str:
    """Hide the password section of a PostgreSQL URL for safe logging."""

    if "@" not in url:
        return url
    prefix, suffix = url.split("@", 1)
    if ":" not in prefix:
        return url
    head, _ = prefix.rsplit(":", 1)
    return f"{head}:******@{suffix}"
