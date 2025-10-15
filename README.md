# 🧑🏽‍🏫 NYU — Lab 06 (DashDash) — Containerised Python + SQL Warehouse

This version of the lab keeps the analytical SQL front-and-centre for students while
moving the orchestration into reusable Python modules. Every object that used to live
inside the monolithic notebook now lives in a dedicated `.sql` file under `warehouse/`.
Learners can focus on the SQL (or swap in dbt later) and simply re-run the pipeline to
rebuild staging, marts, KPIs, monitoring views, tests, and deliverables.

## 📦 Repository layout
- `warehouse/` — **edit me!** Staging/mart/KPI/monitoring SQL plus YAML test configs.
- `src/` — Python helpers for bootstrapping data, connecting to Postgres, executing SQL,
  running tests, and writing the stakeholder deliverable.
- `main.py` — CLI entry point that orchestrates the whole flow.
- `main.ipynb` — Single-cell notebook wrapper around the same pipeline for Codespaces users.
- `Dockerfile` + `docker-compose.yml` — Build/run the lab in a reproducible container.
- `data/` — Seed CSVs (auto-created on first run).
- `outputs/` — Generated exports, stakeholder reply, and `RUN_LOG.txt`.
- `.env` — Default connection string (update per student cohort).

## 🚀 Quick start (local or Codespaces)
```bash
# 1. Ensure credentials are in .env or exported in the shell
export PGHOST=... PGDATABASE=... PGUSER=... PGPASSWORD=...

# 2. Run the orchestrator
python main.py

# or launch the notebook wrapper
devcontainer open .  # in Codespaces
devcontainer exec --workspace-folder . -- python -m pip install -r requirements.txt  # first time
jupyter nbconvert --to notebook --execute main.ipynb  # optional automation
```

At the end of the run you will see:
- `outputs/RUN_LOG.txt` with staged/mart/custom test results (mirrors the old notebook).
- Fresh CSV exports for key views (`stg_orders`, `fct_deliveries`, monitoring, KPI).
- `Lab06_{FIRST}_{LAST}_{NETID}_Reply.md` with the stakeholder summary text.

## 🧰 Docker workflow
```bash
# Build
docker build -t dashdash-lab .

# Run once (uses values from .env)
docker run --rm --env-file .env -v "$(pwd)/outputs:/app/outputs" dashdash-lab
```

`docker-compose.yml` provides the same defaults but exposes the command for iterative runs.

## 🧪 Tests
Data quality checks are defined in YAML + SQL. Modify or extend them in
`warehouse/tests/*.yml` and the pipeline will automatically pick them up.

## 📚 For instructors
- Students only need to touch files in `warehouse/` (SQL) or adjust `.env` for credentials.
- If you prefer dbt, treat `warehouse/` as your source-of-truth SQL models/tests.
- The Python modules in `src/` are intentionally thin wrappers; feel free to extend with
  logging, metrics, or alternate export destinations.

---
_Last updated: 2025-10-08 22:04 UTC_
