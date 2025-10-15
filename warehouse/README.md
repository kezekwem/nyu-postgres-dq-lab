# DashDash Warehouse Layout

This directory collects all of the SQL that students are expected to edit.

```
warehouse/
├── staging/      # staging views used to clean the raw tables
├── marts/        # dimension + fact views
├── kpis/         # metric views surfaced to stakeholders
├── monitoring/   # exception + quality monitoring objects
└── tests/        # SQL-based test queries, grouped by area
```

Each `.sql` file corresponds to a former notebook cell. You can iterate on SQL without
modifying any Python – simply edit the files, save, and re-run `python main.py`
(or the companion notebook) to rebuild the pipeline and collect results. When a
query needs backend-specific syntax we provide an additional file with a
`.sqlite.sql` suffix; the runner automatically picks it when you choose the
SQLite option.

Test configurations live in `tests/*.yml`. The YAML format mirrors dbt's test style:
name, severity, and the SQL file that should return rows when the test fails.
