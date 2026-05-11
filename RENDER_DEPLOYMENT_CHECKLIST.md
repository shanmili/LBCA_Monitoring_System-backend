# RENDER DEPLOYMENT CHECKLIST

## ❌ REQUIRED BACKEND ENVIRONMENT VARIABLES (Set in Render Dashboard)

Go to your Render Backend Service → Environment → Add these variables:

```
ALLOWED_HOSTS=lbca-monitoring-system-backend.onrender.com
SECRET_KEY=your-super-secret-key-here-at-least-50-chars
DEBUG=False
DATABASE_URL=postgresql://[from postgres service]
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
```

### Important Notes:
- **ALLOWED_HOSTS**: Must include your exact Render backend domain (no spaces, exact match)
- **DATABASE_URL**: Copy from your PostgreSQL service on Render
- **SECRET_KEY**: Generate a strong one (e.g., from Django secret key generator)
- **DEBUG**: Must be `False` in production
- **CORS_ALLOWED_ORIGINS**: Already configured in settings.py for your frontend domain

---

## ✅ FRONTEND CONFIGURATION

**File**: `.env`
```
VITE_API_BASE_URL=https://lbca-monitoring-system-backend.onrender.com
VITE_USE_MOCK_FALLBACK=false
```

**Note**: Check that `https://lbca-monitoring-system.onrender.com` is your correct frontend URL on Render

---

## 🔧 BACKEND DJANGO SETUP

**File**: `lbca_backend/settings.py`

Current settings:
- ✅ Reads `ALLOWED_HOSTS` from environment variable
- ✅ Reads `SECRET_KEY` from environment variable
- ✅ Reads `DEBUG` from environment variable
- ✅ Reads `DATABASE_URL` and uses PostgreSQL on Render
- ✅ CORS configured for frontend domain
- ✅ CSRF trusted origins configured

---

## 🚀 DEPLOYMENT STEPS

1. **Set Environment Variables in Render**:
   - Go to Backend Service Settings
   - Environment tab
   - Add all variables from above

2. **Trigger Redeploy**:
   - Push changes to GitHub
   - Render auto-deploys, OR
   - Manually trigger in Render dashboard

3. **Test Backend**:
   ```bash
   curl https://lbca-monitoring-system-backend.onrender.com/api/students/
   # Should return JSON (with 401 if no token, but not HTML error)
   ```

4. **Test Login**:
   ```bash
   curl -X POST https://lbca-monitoring-system-backend.onrender.com/api/teacher/login/ \
     -H "Content-Type: application/json" \
     -d '{"username":"ADMIN001","password":"ADMIN001"}'
   # Should return JSON with token
   ```

---

## ⚠️ COMMON RENDER ERRORS

| Error | Solution |
|-------|----------|
| **HTML instead of JSON** | ALLOWED_HOSTS not set correctly or ALLOWED_HOSTS environment variable missing |
| **502 Bad Gateway** | Backend crashed - check Render logs |
| **CORS Error** | Frontend domain not in CORS_ALLOWED_ORIGINS |
| **Database Connection Error** | DATABASE_URL not set or wrong PostgreSQL service |
| **Static Files 404** | Run `collectstatic` (already in build command) |

---

## 📋 RENDER BACKEND SERVICE SETUP

**Build Command**:
```
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Start Command**:
```
gunicorn lbca_backend.wsgi:application --bind 0.0.0.0:$PORT
```

Both should already be configured if you set up the service initially.

---

## 🔑 HOW TO GET ENVIRONMENT VARIABLES

### SECRET_KEY
Visit: https://djecrety.ir/ or run:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### DATABASE_URL
1. Create PostgreSQL service on Render
2. Copy the connection string from the service details

### ALLOWED_HOSTS
Must match your backend Render URL exactly (from service URL):
Example: `lbca-monitoring-system-backend.onrender.com`

---

## 🧪 VERIFY AFTER DEPLOYMENT

1. Check Render logs for any errors
2. Test endpoint: `https://lbca-monitoring-system-backend.onrender.com/api/`
3. Should see Django REST Framework API root page (HTML is OK here)
4. Try login: `/api/teacher/login/` (POST with credentials)
5. Should return JSON with token

If you get HTML error page instead of JSON → Check ALLOWED_HOSTS environment variable!
