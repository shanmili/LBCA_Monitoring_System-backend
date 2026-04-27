Render deployment guide

1) Add services on Render
- Create a Managed PostgreSQL database. Copy the DATABASE_URL from Render.

2) Create a Web Service for Django
- Connect to this repository and select the branch to deploy (e.g., `main`).
- Environment: Python
- Build Command:
  pip install -r requirements.txt && python manage.py collectstatic --noinput
- Start Command:
  gunicorn lbca_backend.wsgi:application --bind 0.0.0.0:$PORT
- Environment variables (set in Render service settings):
  - DATABASE_URL: (from Postgres service)
  - SECRET_KEY: generate a secure key
  - DEBUG: False
  - ALLOWED_HOSTS: your-service.onrender.com (or * temporarily)
  - CORS_ALLOWED_ORIGINS: https://your-frontend.onrender.com
  - Any other keys used in `lbca_backend/settings.py` (EMAIL settings, etc.)

3) Run migrations and seeder
- Use Render Shell or Post-deploy hook to run once:
  python manage.py migrate
  python django_seed_admin.py

4) Deploy frontend (Static Site)
- Create a Static Site on Render pointing to the frontend repo (or this monorepo's frontend folder).
- Build Command: npm ci && npm run build
- Publish Directory: dist
- Set env var `VITE_API_BASE_URL` to your backend URL (https://your-backend.onrender.com)

5) CORS and static files
- Ensure `django-cors-headers` is configured in `MIDDLEWARE` and `CORS_ALLOWED_ORIGINS` includes your frontend domain.
- `whitenoise` is already present — collectstatic will gather `static/` files.

6) Helpful tips
- Use Render Shell to run one-off commands and inspect logs.
- For automated migration, add a post-deploy hook, but be careful about race conditions.

Commands to run locally before pushing
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python django_seed_admin.py
```
