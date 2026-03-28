-- ============================================================
-- LBCA Monitoring System — MySQL Database Schema
-- Run this ONCE to create the database and tables.
-- Django will manage the tables via migrations after this.
-- ============================================================

CREATE DATABASE IF NOT EXISTS lbca_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE lbca_db;

-- ─── Users ───────────────────────────────────────────────────────────────────
-- Stores all login accounts: admin, teacher, parent
-- For parents (mobile): username = student_id (e.g. S001), password = student_id
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50) NOT NULL UNIQUE,       -- student_id for parents
    email           VARCHAR(254),
    password        VARCHAR(128) NOT NULL,              -- hashed by Django
    role            ENUM('admin','teacher','parent') NOT NULL,
    is_active       TINYINT(1) NOT NULL DEFAULT 1,
    is_staff        TINYINT(1) NOT NULL DEFAULT 0,
    is_superuser    TINYINT(1) NOT NULL DEFAULT 0,
    last_login      DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─── School Years ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS school_years (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    year_label      VARCHAR(20) NOT NULL UNIQUE,        -- e.g. "2025-2026"
    is_current      TINYINT(1) DEFAULT 0
);

-- ─── Teachers ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS teachers (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    middle_name     VARCHAR(50),
    email           VARCHAR(254) NOT NULL UNIQUE,
    employee_id     VARCHAR(20) NOT NULL UNIQUE,
    is_active       TINYINT(1) DEFAULT 1,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Sections ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sections (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,               -- e.g. "Section A", "Faith"
    grade_level     VARCHAR(20) NOT NULL,               -- e.g. "Grade 10"
    adviser_id      INT,
    school_year_id  INT NOT NULL,
    UNIQUE KEY uq_section (name, grade_level, school_year_id),
    FOREIGN KEY (adviser_id)    REFERENCES teachers(id) ON DELETE SET NULL,
    FOREIGN KEY (school_year_id) REFERENCES school_years(id) ON DELETE CASCADE
);

-- ─── Subjects ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS subjects (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,              -- Math, English, Science, Filipino, etc.
    color_hex       VARCHAR(10)                         -- e.g. "#38BDF8"
);

-- ─── Teacher Subject Assignments ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS teacher_subject_assignments (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id      INT NOT NULL,
    subject_id      INT NOT NULL,
    section_id      INT NOT NULL,
    consult_hours   VARCHAR(50),                        -- e.g. "7:30 – 8:30 AM"
    UNIQUE KEY uq_assignment (teacher_id, subject_id, section_id),
    FOREIGN KEY (teacher_id)    REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id)    REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id)    REFERENCES sections(id) ON DELETE CASCADE
);

-- ─── Teacher Availability ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS teacher_availability (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id   INT NOT NULL,
    day             ENUM('Mon','Tue','Wed','Thu','Fri') NOT NULL,
    is_available    TINYINT(1) DEFAULT 1,
    UNIQUE KEY uq_avail (assignment_id, day),
    FOREIGN KEY (assignment_id) REFERENCES teacher_subject_assignments(id) ON DELETE CASCADE
);

-- ─── Students ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id      VARCHAR(20) NOT NULL UNIQUE,        -- e.g. "S001"
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    middle_name     VARCHAR(50),
    date_of_birth   DATE,
    gender          ENUM('Male','Female') NOT NULL,
    address         TEXT,
    section_id      INT,
    school_year_id  INT NOT NULL,
    parent_user_id  INT UNIQUE,                         -- link to users table (role=parent)
    FOREIGN KEY (section_id)        REFERENCES sections(id) ON DELETE SET NULL,
    FOREIGN KEY (school_year_id)    REFERENCES school_years(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_user_id)    REFERENCES users(id) ON DELETE SET NULL
);

-- ─── Guardians ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS guardians (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    student_id_fk       INT NOT NULL UNIQUE,
    first_name          VARCHAR(50) NOT NULL,
    last_name           VARCHAR(50) NOT NULL,
    middle_name         VARCHAR(50),
    contact_number      VARCHAR(20) NOT NULL,
    relationship        ENUM('Father','Mother','Guardian') NOT NULL,
    FOREIGN KEY (student_id_fk) REFERENCES students(id) ON DELETE CASCADE
);

-- ─── Attendance ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attendance (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id_fk   INT NOT NULL,
    date            DATE NOT NULL,
    status          ENUM('present','late','absent') NOT NULL,
    recorded_by_id  INT,
    UNIQUE KEY uq_attendance (student_id_fk, date),
    FOREIGN KEY (student_id_fk)     REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by_id)    REFERENCES teachers(id) ON DELETE SET NULL
);

-- ─── PACE Records ─────────────────────────────────────────────────────────────
-- One row per PACE booklet per student per subject per quarter
CREATE TABLE IF NOT EXISTS pace_records (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id_fk   INT NOT NULL,
    subject_id      INT NOT NULL,
    quarter         TINYINT NOT NULL,                   -- 1, 2, 3, or 4
    pace_number     TINYINT NOT NULL,                   -- PACE booklet #
    completed       TINYINT(1) DEFAULT 0,
    test_score      FLOAT,
    recorded_by_id  INT,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_pace (student_id_fk, subject_id, quarter, pace_number),
    FOREIGN KEY (student_id_fk)     REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id)        REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by_id)    REFERENCES teachers(id) ON DELETE SET NULL
);

-- ─── Grades ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS grades (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id_fk   INT NOT NULL,
    subject_id      INT NOT NULL,
    quarter         TINYINT NOT NULL,
    grade_value     FLOAT,
    school_year_id  INT NOT NULL,
    recorded_by_id  INT,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_grade (student_id_fk, subject_id, quarter, school_year_id),
    FOREIGN KEY (student_id_fk)     REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id)        REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (school_year_id)    REFERENCES school_years(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by_id)    REFERENCES teachers(id) ON DELETE SET NULL
);

-- ─── Risk Assessments ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS risk_assessments (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    student_id_fk       INT NOT NULL,
    assessed_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    risk_level          ENUM('low','moderate','high','critical') NOT NULL,
    status              ENUM('On Track','Behind','At Risk','Critical') NOT NULL,
    pace_percent        FLOAT NOT NULL,
    attendance_percent  FLOAT NOT NULL,
    trend               ENUM('improving','stable','declining') DEFAULT 'stable',
    primary_factor      VARCHAR(200),
    secondary_factor    VARCHAR(200),
    suggested_action    VARCHAR(200),
    paces_behind        INT DEFAULT 0,
    is_latest           TINYINT(1) DEFAULT 1,           -- only one TRUE per student
    FOREIGN KEY (student_id_fk) REFERENCES students(id) ON DELETE CASCADE
);

-- ─── Notifications ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notifications (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    recipient_id        INT NOT NULL,
    notification_type   ENUM('grade','alert','announcement','schedule') NOT NULL,
    title               VARCHAR(200) NOT NULL,
    body                TEXT NOT NULL,
    is_read             TINYINT(1) DEFAULT 0,
    route               VARCHAR(50),                    -- mobile tab route
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Activity Logs ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activity_logs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    log_type        ENUM('alert','pace','attendance','risk','system') NOT NULL,
    text            VARCHAR(300) NOT NULL,
    created_by_id   INT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ─── Django System Tables (managed by Django, listed for reference) ────────────
-- auth_group, auth_group_permissions, auth_permission
-- core_user_groups, core_user_user_permissions
-- django_admin_log, django_content_type, django_migrations, django_session

-- ============================================================
-- SAMPLE SEED DATA
-- ============================================================

-- School Year
INSERT IGNORE INTO school_years (year_label, is_current) VALUES ('2025-2026', 1);

-- Subjects
INSERT IGNORE INTO subjects (name, color_hex) VALUES
  ('Mathematics',        '#38BDF8'),
  ('English',            '#34D399'),
  ('Science',            '#A78BFA'),
  ('Filipino',           '#FBBF24'),
  ('Araling Panlipunan', '#F87171'),
  ('MAPEH',              '#FB923C');

-- NOTE: User passwords and student records must be created via Django
-- (python manage.py createsuperuser) or via /api/auth/register/
-- because Django hashes passwords before storing them.

-- ============================================================
-- HOW PARENT LOGIN WORKS
-- ============================================================
-- 1. Admin creates a User with role='parent', username=student_id, password=student_id
--    via Django admin or /api/auth/register/
-- 2. Admin links that user to the student record (parent_user_id)
-- 3. Parent opens the mobile app, enters student_id in both EMAIL and PASSWORD fields
-- 4. App hits POST /api/auth/login/ with { username: "S001", password: "S001" }
-- 5. Backend returns JWT access token + student info
