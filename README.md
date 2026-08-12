# MAT Legal Network

Flask + Jinja + PostgreSQL application scaffold using an application factory, blueprints, SQLAlchemy, Alembic (Flask-Migrate), and Docker Compose.

## Stack

- Flask (application factory + blueprints)
- Jinja2 templates
- PostgreSQL via Flask-SQLAlchemy + Flask-Migrate
- Docker Compose (`web` + `db`)
- Health API: `GET /api/health`

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

- App: http://localhost:5000
- Health: http://localhost:5000/api/health

## Local development

1. Start Postgres (or use Compose: `docker compose up db -d`).
2. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

3. Point `DATABASE_URL` in `.env` at local Postgres, for example:

```text
DATABASE_URL=postgresql+psycopg://mat:mat@localhost:5432/mat_legal
```

4. Run migrations and start the app:

```bash
flask --app wsgi:app db upgrade
python run.py
```

## Migrations

```bash
flask --app wsgi:app db migrate -m "describe change"
flask --app wsgi:app db upgrade
```

## Tests

```bash
pytest
```

Tests use an in-memory SQLite database (`FLASK_ENV=testing`).

## Project layout

```text
app/
  __init__.py          # create_app()
  config.py
  extensions.py
  models/
  blueprints/
    main/              # Jinja home page
    api/               # /api/health
  templates/
  static/
migrations/
tests/
wsgi.py
run.py
Dockerfile
docker-compose.yml
```
