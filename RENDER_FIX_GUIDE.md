# 🔧 Complete Render Login & CORS Fix

## 🚨 Current Issue
- ✅ Backend is deployed and responding to `/api/`
- ❌ Login endpoint returns 500 error (likely database/seed issue)
- ❌ Frontend can't log in

---

## ✅ STEP-BY-STEP FIX

### **STEP 1: Verify Environment Variables on Render**

Go to **Render Dashboard** → Your **Backend Service** → **Settings** → **Environment**

Ensure ALL these are set:

```env
ALLOWED_HOSTS=lbca-monitoring-system-backend.onrender.com
DEBUG=False
SECRET_KEY=<your-secret-key-here>
DATABASE_URL=postgresql://...
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=31536000
```

> ⚠️ **IMPORTANT**: Replace `lbca-monitoring-system-backend.onrender.com` with your EXACT Render domain

---

### **STEP 2: Run Database Migrations & Seed Admin** (WITHOUT Shell Access)

**Option A: Using Initialization Endpoint (EASIEST - No Shell Needed)**

This is the best solution for free Render accounts!

1. First, set an initialization key in Render environment variables:
   - Go to **Backend Service** → **Settings** → **Environment**
   - Add: `INIT_SECRET_KEY=your-super-secret-init-key-12345` (make it random/unique)

2. Push your code to GitHub (includes the new `init_views.py`)

3. Once deployed, call the initialization endpoint:

```powershell
$initKey = "your-super-secret-init-key-12345"
$body = @{init_key=$initKey} | ConvertTo-Json
$uri = "https://lbca-monitoring-system-backend.onrender.com/api/init/database/"
$response = Invoke-WebRequest -Uri $uri -Method POST -ContentType "application/json" -Body $body -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json
```

Expected response:
```json
{
  "status": "Database initialization completed",
  "migrations": "✓ Migrations completed",
  "seed": "✓ Seed data created",
  "next_steps": [...]
}
```

4. Check status anytime:
```powershell
Invoke-WebRequest -Uri "https://lbca-monitoring-system-backend.onrender.com/api/init/status/" -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

**Option B: Using Post-Deploy Hook (Automatic)**

If you have a `render.yaml` file in your repo root, Render will use it instead of manual config.

The hook will run automatically on each deployment:
```yaml
preDeployCommand: python manage.py migrate && python django_seed_admin.py
```

---

### **STEP 2 (OLD): Using Render Shell** (Requires Pro Account)

⚠️ **NOT AVAILABLE** on free tier - use Option A above instead.

---

### **STEP 3: Test Login from Render Shell**

```bash
python manage.py shell
```

Then in the Python shell:

```python
from django.contrib.auth import authenticate
user = authenticate(username='ADMIN001', password='ADMIN001')
print(f"Authentication result: {user}")
if user:
    print(f"User: {user.username}")
    print(f"Has teacher profile: {hasattr(user, 'teacher_profile')}")
```

---

### **STEP 4: Test Backend Login Endpoint**

From your local machine:

```powershell
$body = @{username="ADMIN001"; password="ADMIN001"} | ConvertTo-Json
$uri = "https://lbca-monitoring-system-backend.onrender.com/api/teacher/login/"
Invoke-WebRequest -Uri $uri -Method POST -ContentType "application/json" -Body $body -UseBasicParsing
```

**Expected response:**
```json
{
  "message": "Teacher login successful",
  "token": "abc123...",
  "username": "ADMIN001",
  "role": "Admin",
  ...
}
```

---

### **STEP 5: Update Frontend VITE_API_BASE_URL**

**For Render Frontend Service:**
- Go to **Settings** → **Environment**
- Add/update:

```env
VITE_API_BASE_URL=https://lbca-monitoring-system-backend.onrender.com
VITE_USE_MOCK_FALLBACK=false
```

> ⚠️ Use `https://` (not `http://`) - Render requires HTTPS

**For Local Frontend Development:**
- Create/update `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK_FALLBACK=false
```

---

### **STEP 6: Frontend Fetch Configuration**

Ensure your frontend fetch calls include CORS headers:

```javascript
// Example: src/api/client.js or AuthController.jsx
const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/teacher/login/`, {
  method: 'POST',
  mode: 'cors',
  credentials: 'include',
  headers: { 
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ username, password }),
});

const data = await response.json();
```

---

## 🔍 Debugging Checklist

| Issue | Check |
|-------|-------|
| **Still getting HTML instead of JSON** | 1. Verify `ALLOWED_HOSTS` is set exactly right<br>2. Redeploy backend: push code or manually trigger in Render<br>3. Check Render logs for 404/500 errors |
| **Login returns 500 error** | 1. Run migrations: `python manage.py migrate`<br>2. Run seeder: `python django_seed_admin.py`<br>3. Check database connection |
| **CORS error in browser console** | 1. Frontend URL must be in `CORS_ALLOWED_ORIGINS`<br>2. Frontend fetch must include `mode: 'cors'`<br>3. Check console for exact domain mismatch |
| **"Invalid credentials" on login** | 1. Verify admin exists: `python manage.py shell`<br>2. Check username/password are correct<br>3. Check teacher account status is 'Active' |

---

## 📝 Quick Command Reference

### Local Testing
```powershell
# Activate venv
.venv\Scripts\Activate.ps1

# Run migrations
python manage.py migrate

# Run seeder
python django_seed_admin.py

# Run server
python manage.py runserver
```

### Render Shell Commands
```bash
# Migrations
python manage.py migrate

# Seed admin
python django_seed_admin.py

# Check users
python manage.py shell
# Then: from django.contrib.auth.models import User; User.objects.all()
```

---

## ✅ Success Indicators

- ✅ `/api/` returns JSON (not HTML)
- ✅ `/api/teacher/login/` with valid credentials returns token
- ✅ Frontend can log in successfully
- ✅ Browser console shows no CORS errors
- ✅ Network tab shows responses as `application/json` (not `text/html`)

---

## 🆘 Still Having Issues?

1. **Check Render Logs**: Backend Service → Logs → check for errors
2. **Run this locally first**: Test everything works locally before deploying
3. **Verify database**: `python manage.py dbshell` to check connection
4. **Check network tab**: In browser DevTools, verify request/response headers
