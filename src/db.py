"""Database connection and schema management helpers."""
from __future__ import annotations

from contextlib import contextmanager
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .config import Settings, mask_url

logger = logging.getLogger(__name__)


class EngineFactory:
    """Create and cache a SQLAlchemy engine from the current settings."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._engine: Engine | None = None

    @property
    def settings(self) -> Settings:
        return self._settings

    def get_engine(self) -> Engine:
        if self._engine is None:
            logger.info("Creating SQLAlchemy engine for %s", mask_url(self._settings.database_url))
            self._engine = create_engine(
                self._settings.database_url,
                echo=False,
                future=True,
                pool_pre_ping=True,
            )
        return self._engine

    @property
    def dialect(self) -> str:
        return self.get_engine().dialect.name

    @contextmanager
    def connect(self):
        engine = self.get_engine()
        conn = engine.connect()
        try:
            yield conn
        finally:
            conn.close()

    def dispose(self) -> None:
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None


def set_search_path_safely(factory: EngineFactory) -> None:
    """Ensure learners operate inside their personal schema (mirrors notebook safety block)."""

    if factory.dialect == "sqlite":
        return

    safety_block = """
    SET search_path TO "$user", public;
    DO $$
    DECLARE
      current_schema_name text := current_schema();
      current_user_name   text := current_user;
      is_instructor       boolean := has_schema_privilege(current_user, 'public', 'CREATE');
    BEGIN
      IF current_schema_name <> current_user_name
         AND NOT (is_instructor AND current_schema_name = 'public') THEN
        RAISE EXCEPTION
          'You are in schema "%", not your personal schema "%". Run: SET search_path TO "$user", public;',
          current_schema_name, current_user_name;
      END IF;

      IF is_instructor AND current_schema_name = 'public' THEN
        RAISE NOTICE 'Instructor mode: running as "%" in schema "public".', current_user_name;
      END IF;
    END $$;
    """

    with factory.connect() as conn:
        conn.execute(text(safety_block))
        conn.commit()


def ensure_schema_exists(factory: EngineFactory, schema: str) -> None:
    with factory.connect() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}";'))
        conn.execute(text(f'GRANT USAGE, CREATE ON SCHEMA "{schema}" TO "{schema}";'))
        conn.commit()


def smoke_test(factory: EngineFactory) -> None:
    """Run lightweight queries that mimic the notebook diagnostics."""

    if factory.dialect == "sqlite":
        with factory.connect() as conn:
            current_date = conn.execute(text("SELECT date('now')"))
            current_date = current_date.scalar_one()
        logger.info("Connected to SQLite — current_date=%s database=%s", current_date, factory.settings.database_url)
        return

    with factory.connect() as conn:
        current_date = conn.execute(text("SELECT current_date")).scalar_one()
        current_user, current_schema = conn.execute(
            text("SELECT current_user, current_schema")
        ).first()
    logger.info(
        "Connected to Postgres — current_date=%s user=%s schema=%s",
        current_date,
        current_user,
        current_schema,
    )
