# Deploying ContactBook to Render

This project is now configured to deploy on Render with Render PostgreSQL.

## What changed

- **`requirements.txt`** — pinned dependencies: `django`, `gunicorn` (app
  server), `psycopg[binary]` (Postgres driver), `dj-database-url` (parses
  Render's `DATABASE_URL`), `whitenoise` (serves static files), `python-dotenv`
  (loads `.env` locally).
- **`ContactBook/settings.py`**
  - `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` now come
    from environment variables instead of being hardcoded.
  - `DATABASES` uses `DATABASE_URL` when set (Render Postgres), and falls
    back to local SQLite when it isn't (so local dev needs no extra setup).
  - Added `whitenoise` middleware + `STATIC_ROOT`/`STORAGES` so
    `collectstatic` produces compressed, cache-busted static files servable
    directly by gunicorn — no separate static host needed.
  - Added standard production hardening (`SECURE_SSL_REDIRECT`,
    secure cookies) when `DEBUG=False`.
- **`build.sh`** — Render's build command: installs deps, runs
  `collectstatic`, runs `migrate`.
- **`Procfile`** / **`render.yaml`** — start command
  (`gunicorn ContactBook.wsgi:application`) and an optional one-click
  Blueprint spec that provisions a free Postgres DB + web service together.
- **`.gitignore`** — stops `db.sqlite3`, `__pycache__/`, `staticfiles/`,
  and `.env` from being committed.
- Removed the committed `db.sqlite3` and `__pycache__` files (these should
  never be in version control — Render's Postgres database is your real
  data store now).

## Deploy steps

### Option A — Blueprint (`render.yaml`), one click

1. Push this repo to GitHub/GitLab.
2. In the Render dashboard: **New > Blueprint**, point it at the repo.
3. Render reads `render.yaml` and provisions both the Postgres database
   (`contactbook-db`) and the web service (`contactbook`) together, wiring
   `DATABASE_URL` automatically.
4. Click **Apply** — first deploy runs `build.sh` then starts gunicorn.

### Option B — Manual setup

1. **New > PostgreSQL** in Render. Note the **Internal Database URL**.
2. **New > Web Service**, point it at this repo.
   - Runtime: Python 3
   - Build Command: `./build.sh`
   - Start Command: `gunicorn ContactBook.wsgi:application`
3. Under the service's **Environment** tab, add:
   | Key | Value |
   |---|---|
   | `SECRET_KEY` | (generate a random 50-char string) |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `.onrender.com` (or your custom domain) |
   | `DATABASE_URL` | the Internal Database URL from step 1 |
4. Deploy. Render runs `build.sh` (installs deps, collects static files,
   applies migrations), then starts the app with gunicorn.

## After first deploy

Create an admin user for `/admin/` (Render dashboard → your service →
**Shell**):

```bash
python manage.py createsuperuser
```

## Local development

```bash
cp .env.example .env         # edit values as needed
pip install -r requirements.txt
python manage.py migrate     # uses local SQLite since DATABASE_URL is unset
python manage.py runserver
```

To test against Postgres locally too, just set `DATABASE_URL` in `.env` to
Render's **External Database URL** (or a local Postgres instance).

## Note on password storage

`login/views.py` currently compares plaintext passwords stored on the
custom `User` model directly, rather than using Django's built-in
`auth.User` with hashed passwords. This works but is not secure for a
real deployment with real user data — worth revisiting separately from
this Render setup (e.g. via `django.contrib.auth.hashers.make_password`/
`check_password`, or migrating to Django's built-in auth system).
