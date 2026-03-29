# LBCA Monitoring System — Backend

A Django REST Framework backend for the LBCA Student Monitoring System. This system manages students, teachers, enrollments, scheduling, and academic tracking.

---

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Framework:** Django + Django REST Framework
- **Database:** SQLite (development) — replaceable with PostgreSQL for production
- **Auth:** Django built-in User model

---

## 📁 Project Structure

```
LBCA_Monitoring_System-backend/
├── lbca_backend/           # Main Django project settings
├── grade_levels/           # Grade level management
├── school_years/           # School year management
├── sections/               # Section management
├── teachers/               # Teacher profiles & availability
├── students/               # Student profiles & enrollments
├── student_pace/           # Student pace tracking
├── data_quality_log/       # Data quality logging
├── manage.py
└── db.sqlite3
```

---

## 👥 Team & Module Ownership

| App | Description | Owner |
|-----|-------------|-------|
| `grade_levels` | Grade level records | *SEF* |
| `school_years` | School year records | *SEF* |
| `sections` | Section records | *SEF* |
| `teachers` | Teacher profiles, assignments, availability | *NOR & KEYB* |
| `students` | Student profiles + enrollments | *SHAN* |
| `student_pace` | Pace tracking per student | *SHAN* |
| `data_quality_log` | Logging data issues | *NOR* |

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/shanmili/LBCA_Monitoring_System-backend.git
cd LBCA_Monitoring_System-backend
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install django djangorestframework
```

> If a `requirements.txt` exists:
> ```bash
> pip install -r requirements.txt
> ```

### 4. Apply migrations
```bash
python manage.py migrate
```

### 5. Create a superuser (optional, for admin access)
```bash
python manage.py createsuperuser
```

### 6. Run the development server
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

---

## 🗄️ Database Schema (ERD Summary)

Key relationships:
- A **Student** belongs to a **User** account (OneToOne)
- A **StudentEnrollment** links a Student → GradeLevel → Section → SchoolYear
- A **Teacher** can be assigned to multiple Subjects and Sections via **TeacherAssignments**
- **StudentPace** tracks individual student progress per school year
- **DataQualityLog** records issues flagged against student/teacher records

---

## 📌 API Endpoints (per app)

Each app exposes standard REST endpoints via Django REST Framework routers:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/students/` | List all students |
| POST | `/api/students/` | Create a student |
| GET | `/api/students/{id}/` | Retrieve a student |
| PUT/PATCH | `/api/students/{id}/` | Update a student |
| DELETE | `/api/students/{id}/` | Delete a student |
| GET | `/api/enrollments/` | List all enrollments |
| POST | `/api/enrollments/` | Create an enrollment |

*(Other apps follow the same pattern)*

---

## 🤝 Contributing (For Teammates)

1. Pull the latest changes before starting work:
   ```bash
   git pull origin main
   ```
2. Work only on your assigned app/module.
3. Run migrations after pulling if models changed:
   ```bash
   python manage.py migrate
   ```
4. Do not modify another teammate's models without coordinating first.

---

## 📝 Notes

- Foreign keys that cross apps (e.g., `students` referencing `grade_levels`) use Django's `'app_name.ModelName'` string format.
- Always run `makemigrations <your_app>` when you change your own models:
  ```bash
  python manage.py makemigrations students
  python manage.py migrate
  ```