**Purpose**

This file describes how to set up, run, test, and contribute to the Mersa task manager repository.

**Quick Setup**

- **Python**: Use Python 3.10+ (3.11 recommended). Create and activate a venv.

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Unix
source .venv/bin/activate
pip install -r requirements.txt
```

- Copy environment variables from `.env.example` or create a `.env` file; set `SECRET_KEY`, `DATABASE_URL`, etc.

**Database & Migrations**

- Apply migrations after installing requirements:

```bash
py manage.py migrate
```

- Important: the repository contains schema changes that add Workspaces and run a backfill migration.
  If you encounter NOT NULL constraint errors during `migrate`, make sure you have the full migration set (including `task_manager/migrations/0004_workspace_rbac.py`, `0005_backfill_workspace.py`, and `0006_alter_task_workspace.py`) and re-run `migrate`.

- If you modify models, create migrations and include them in your PR:

```bash
py manage.py makemigrations
py manage.py migrate
```

**Front-end assets**

- The dashboard uses Chart.js and ProgressBar.js. The project includes copies under `static/` by default.
- To use CDN instead, edit the template at [templates/task_manager/index.html](templates/task_manager/index.html) and replace the `{% static %}` script tags with CDN URLs.

**Running the app**

```bash
py manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

**Tests & Linting**

- Run tests with `pytest`:

```bash
pytest
```

- Linting (optional): `flake8` is included in `requirements.txt`.

**What to include in a PR**

- A clear description of the change.
- Any new migrations (run `makemigrations`) and a short note about data/backfill if relevant.
- Tests that cover new behavior or bug fixes.
- If you changed front-end assets, either check in the files under `static/` or update the template to reference a known CDN.

**Notes about RBAC and Workspaces**

- The project now uses `Workspace` and `WorkspaceMembership` models to scope tasks and permissions. Avoid removing those models or their migrations unless you also provide a safe migration/backfill plan.
- The `Task.workspace` field was backfilled and then made non-nullable — be careful when altering this field.

**Developer tips**

- If you add or change JS that is loaded on the dashboard, confirm that `window.DASHBOARD_DATA` keys are still provided by `task_manager.views.index`.
- `Worker.visit_count` was added (migration `0008_add_visit_count.py`) for visitor metrics. If you reset the DB, re-run migrations to add this field.

**Contact / Questions**

Open an issue or leave a comment on the PR describing the problem and environment (Python version, OS, steps to reproduce).

Thank you for contributing!
