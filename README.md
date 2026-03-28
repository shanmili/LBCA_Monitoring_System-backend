# LBCA Monitoring System — Backend (Django REST Framework)

Backend API for the **Lapasan Baptist Christian Academy (LBCA) Monitoring System**.  
Supports both the **web admin/teacher dashboard** (React) and the **parent mobile app** (React Native / Expo).

---

## Tech Stack
- **Python 3.x** + **Django 5.x**
- **Django REST Framework (DRF)**
- **Simple JWT** — token-based authentication
- **MySQL** — database
- **django-cors-headers** — for cross-origin requests

---

## Setup

### 1. Create MySQL Database
```sql
mysql -u root -p < lbca_schema.sql
```

### 2. Install Dependencies
```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers mysqlclient
```

### 3. Configure Database
Edit `lbca_backend/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lbca_db',
        'USER': 'root',
        'PASSWORD': 'yourpassword',  # ← change this
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Admin)
```bash
python manage.py createsuperuser
# username: admin, password: admin123
```

### 6. Run Server
```bash
python manage.py runserver
```

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login (all roles) |
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/logout/` | Logout (blacklist token) |
| GET  | `/api/auth/me/` | Current user info |
| POST | `/api/auth/token/refresh/` | Refresh JWT |

### Dashboard (Admin/Teacher — Web)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats/` | KPI cards (totals, at-risk, pace%) |
| GET | `/api/dashboard/activity/` | Activity feed |

### Students (Admin/Teacher — Web)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/students/` | List all students |
| POST | `/api/students/` | Add student |
| GET  | `/api/students/<student_id>/` | Student full detail |
| PUT  | `/api/students/<student_id>/` | Update student |
| DELETE | `/api/students/<student_id>/` | Remove student |

### Risk / Early Warning
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/risk/at-risk/` | All at-risk students |
| GET | `/api/risk/student/<student_id>/` | Risk history for one student |

### PACE
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/pace/` | List PACE records (filter: student_id, subject, quarter, section) |
| POST | `/api/pace/` | Record PACE completion/score |

### Grades
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/grades/` | List grades (filter: student_id, quarter) |
| POST | `/api/grades/` | Add/update grade |

### Attendance
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/attendance/` | List attendance (filter: student_id, month) |
| POST | `/api/attendance/` | Record attendance |

### Teachers (Admin — Web)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/teachers/` | List teachers |
| POST   | `/api/teachers/` | Add teacher |
| GET    | `/api/teachers/<id>/` | Teacher detail |
| PUT    | `/api/teachers/<id>/` | Update teacher |
| DELETE | `/api/teachers/<id>/` | Remove teacher |

### Lookup
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sections/` | All sections |
| GET | `/api/subjects/` | All subjects |

### Notifications (Parent — Mobile)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/notifications/` | My notifications |
| POST | `/api/notifications/<id>/read/` | Mark one as read |
| POST | `/api/notifications/mark-all-read/` | Mark all read |

### Parent / Mobile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/parent/my-student/` | Linked student full profile |
| GET | `/api/parent/grades/` | My child's grades (filter: quarter) |
| GET | `/api/parent/attendance/` | My child's attendance (filter: month) |
| GET | `/api/parent/pace/` | My child's PACE records (filter: quarter) |
| GET | `/api/parent/risk/` | My child's latest risk assessment |

---

## Authentication

All endpoints (except login/register) require a Bearer token:
```
Authorization: Bearer <access_token>
```

### Login Examples (httpie)

**Web — Teacher:**
```bash
http POST http://127.0.0.1:8000/api/auth/login/ username="teacher@lbca.edu" password="teacher123"
```

**Web — Admin:**
```bash
http POST http://127.0.0.1:8000/api/auth/login/ username="admin@lbca.edu" password="admin123"
```

**Mobile — Parent (student_id as both username and password):**
```bash
http POST http://127.0.0.1:8000/api/auth/login/ username="S001" password="S001"
```

---

## Testing APIs with httpie

```bash
# Get JWT token first
TOKEN=$(http POST http://127.0.0.1:8000/api/auth/login/ username="admin@lbca.edu" password="admin123" | python -c "import sys,json; print(json.load(sys.stdin)['access'])")

# Dashboard stats
http GET http://127.0.0.1:8000/api/dashboard/stats/ "Authorization: Bearer $TOKEN"

# Students list
http GET http://127.0.0.1:8000/api/students/ "Authorization: Bearer $TOKEN"

# At-risk students
http GET http://127.0.0.1:8000/api/risk/at-risk/ "Authorization: Bearer $TOKEN"

# Student detail
http GET http://127.0.0.1:8000/api/students/S001/ "Authorization: Bearer $TOKEN"

# Parent login and view child
http POST http://127.0.0.1:8000/api/auth/login/ username="S001" password="S001"
http GET http://127.0.0.1:8000/api/parent/my-student/ "Authorization: Bearer <parent_token>"
```

---

## Database Design

### Key Tables
| Table | Purpose |
|-------|---------|
| `users` | All accounts — admin, teacher, parent (mobile) |
| `teachers` | Teacher profile + linked user account |
| `students` | Student records with section/guardian info |
| `guardians` | Parent/guardian contact info per student |
| `sections` | Grade sections (Section A, Faith, Hope...) |
| `subjects` | Subjects (Math, English, Science...) |
| `pace_records` | PACE booklet completion + test scores |
| `grades` | Quarterly grades per subject |
| `attendance` | Daily attendance records |
| `risk_assessments` | Early warning risk flags per student |
| `notifications` | Push-style notifications for parents |
| `activity_logs` | Admin dashboard activity feed |

### Parent Login Logic
1. Admin creates a `User` with `role='parent'`, `username=<student_id>`, `password=<student_id>`
2. Admin links that user to the `Student` record via `parent_user_id`
3. Parent opens mobile app → enters **Student ID** in both the email and password fields
4. App sends `POST /api/auth/login/` with `{ username: "S001", password: "S001" }`
5. API returns JWT token + student profile data

---

## Commit Message (as required)
```
AppDev: DRF backend for system implemented
```
