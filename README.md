# 🧑🏽‍🏫 NYU — Lab 06 (DashDash) — **All-Python + PostgreSQL** (Codespaces Ready)

This repo runs **cleanly in GitHub Codespaces** (or locally) and replaces the dbt steps with equivalent **pure Python** logic
using SQLAlchemy + pandas **against PostgreSQL**.

## 📦 What’s inside
- `lab06_python_postgres_codespaces.ipynb` — the complete lab in a single notebook:
  - Bootstrap + dependency checks (rich logs, timers, archiving)
  - CSV creation/load (with small intentional defects for DQ testing)
  - Staging **views**: normalization, dedupe, derived fields
  - Data Quality tests: not_null, unique, accepted_values, relationships, expression checks
  - Marts: `fct_deliveries` + thin dims
  - KPIs: `kpi_delivery_overview`
  - Monitoring: `monitoring_dq_exceptions`
  - Self-solve test: `test_dropoff_status_logic`
  - Deliverable writer: Markdown stakeholder reply
- `data/` — four CSVs: `orders.csv`, `restaurants.csv`, `couriers.csv`, `customers.csv`
- `outputs/` — created at runtime for exports and `RUN_LOG.txt`
- `.gitignore` — ignores Python/Notebook cache and `/outputs` (you can remove if you want exports tracked)

## 🚦 Quick Start (Codespaces)
1) Click **Use this template → Create a new repository**.
2) Open the repo → **Code → Codespaces → Create codespace on main**.
3) Open `lab06_python_postgres_codespaces.ipynb`.
4) Fill in your Postgres credentials in **Block02-Config** (or set `DATABASE_URL` in Codespaces secrets).
5) Run all cells top-to-bottom.

> **Student connection placeholders:** in Block02, edit `PGHOST`, `PGDATABASE`, `PGUSER`, `PGPASSWORD` or provide a `DATABASE_URL`.
> **Instructor:** set `DB_MODE="admin"` and demonstrate from the `public` schema (if you have CREATE privilege).

## 🗃️ Data & DB
- The notebook seeds the `data/*.csv` into **tables** in your personal schema (search_path is locked to `$user`, with a safe admin override).
- Staging is implemented as **SQL views** to keep logic transparent and re-runnable.

## 🧑🏽‍🏫 Instructor notes
- If you already provisioned per-student roles/schemas, students can just supply their username/password and run the notebook.
- The DQ tests write failing rows to `dq_failures__*` tables for review.
- A consolidated test summary is appended to `outputs/RUN_LOG.txt` for grading.
- To swap in your official CSVs, replace the files in `data/` before students run Block03.

## 🧰 Local (optional)
- Python 3.11 recommended
- `pip install sqlalchemy psycopg2-binary pandas rich python-dotenv ipywidgets`
- `jupyter lab` then open the notebook

## 🤖 AI policy
AI help for wording/boilerplate is allowed. Disclose the model/date in your Markdown reply. Students are responsible for understanding the code they submit.

---
_Last updated: 2025-10-08 22:04 UTC_
