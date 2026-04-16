# LBCA Monitoring System - REST API Endpoints

## Overview
All endpoints follow strict REST conventions with standard HTTP methods on consolidated resource paths.
- Base URL: `http://localhost:8000/api/` or `http://localhost:8000/api/v1/`
- Authentication: Token-based (Bearer token in Authorization header)
- Response Format: JSON
- Pagination: Enabled with `?page=1` query parameter (default page_size=10)

---

## 1. AUTHENTICATION ENDPOINTS (Custom Actions)

### Admin Registration
**POST** `/api/admin/register/`
- **Description**: Admin self-registration with auto-generated username (ADMIN001, ADMIN002, etc.)
- **Body**:
  ```json
  {
    "first_name": "John",
    "last_name": "Admin",
    "email": "john@example.com",
    "password": "secure_password"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "message": "Admin account created successfully",
    "token": "abc123...",
    "username": "ADMIN001",
    "teacher_id": 1,
    "role": "Admin",
    "first_name": "John",
    "last_name": "Admin",
    "is_first_login": true
  }
  ```

### Admin Login
**POST** `/api/admin/login/`
- **Description**: Admin login using username and password
- **Body**:
  ```json
  {
    "username": "ADMIN001",
    "password": "secure_password"
  }
  ```
- **Response**: `200 OK` (same as registration response)

### Teacher Login
**POST** `/api/teacher/login/`
- **Description**: Teacher/Admin login using username (TCH001, ADMIN001, etc.) and password
- **Body**:
  ```json
  {
    "username": "TCH001",
    "password": "TCH001"
  }
  ```
- **Response**: `200 OK` (same as admin login)

### Teacher Logout
**POST** `/api/teacher/logout/`
- **Description**: Logout and invalidate authentication token
- **Auth Required**: Yes (Bearer token)
- **Response**: `200 OK`
  ```json
  {
    "message": "Logout successful"
  }
  ```

---

## 2. TEACHER MANAGEMENT (REST CRUD)

### List Teachers
**GET** `/api/teachers/`
- **Description**: List all teachers (Admin only)
- **Auth Required**: Yes (Bearer token + Admin role)
- **Query Parameters**: None
- **Response**: `200 OK` (paginated array)
  ```json
  {
    "count": 25,
    "next": "http://localhost:8000/api/teachers/?page=2",
    "previous": null,
    "results": [
      {
        "teacher_id": 1,
        "user": {
          "username": "TCH001",
          "email": "teacher@example.com",
          "first_name": "John",
          "last_name": "Doe"
        },
        "role": "Teacher",
        "department": "Mathematics",
        "status": "Active",
        "is_first_login": true
      }
    ]
  }
  ```

### Create Teacher
**POST** `/api/teachers/`
- **Description**: Create teacher account with auto-generated username (TCH001, TCH002, etc.) (Admin only)
- **Auth Required**: Yes (Bearer token + Admin role)
- **Body**:
  ```json
  {
    "role": "Teacher",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com",
    "department": "Chemistry"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "message": "Teacher account created successfully",
    "teacher_id": 2,
    "username": "TCH002",
    "password": "TCH002",
    "is_first_login": true
  }
  ```

### Retrieve Teacher
**GET** `/api/teachers/{id}/`
- **Description**: Retrieve single teacher details
- **Auth Required**: Yes (Bearer token)
- **Response**: `200 OK` (single teacher object)

### Update Teacher (Full)
**PUT** `/api/teachers/{id}/`
- **Description**: Full update of teacher (all fields required, Admin only)
- **Auth Required**: Yes (Bearer token + Admin role)
- **Body**: Same structure as Create Teacher
- **Response**: `200 OK` (updated teacher object)

### Update Teacher (Partial)
**PATCH** `/api/teachers/{id}/`
- **Description**: Partial update of teacher (Admin only)
- **Auth Required**: Yes (Bearer token + Admin role)
- **Body**: Any subset of teacher fields
- **Response**: `200 OK` (updated teacher object)

### Deactivate Teacher
**DELETE** `/api/teachers/{id}/`
- **Description**: Soft delete (deactivate) teacher by setting status to Inactive (Admin only)
- **Auth Required**: Yes (Bearer token + Admin role)
- **Response**: `200 OK`
  ```json
  {
    "message": "Teacher TCH001 deactivated successfully",
    "teacher_id": 1,
    "username": "TCH001",
    "status": "Inactive"
  }
  ```

### Reactivate Teacher
**PATCH** `/api/teachers/{id}/reactivate/`
- **Description**: Reactivate deactivated teacher by setting status to Active (Admin only)
- **Auth Required**: Yes (Bearer token + Admin role)
- **Response**: `200 OK` (same format as deactivate)

---

## 3. TEACHER PROFILE (Custom Actions)

### Get Current Teacher Profile
**GET** `/api/teacher/profile/`
- **Description**: Get logged-in teacher's profile information
- **Auth Required**: Yes (Bearer token)
- **Response**: `200 OK` (teacher object)

### Update Current Teacher Profile
**PUT/PATCH** `/api/teacher/profile/update/`
- **Description**: Update own profile details (name, email, password, etc.)
- **Auth Required**: Yes (Bearer token)
- **Body**:
  ```json
  {
    "first_name": "Updated",
    "email": "newemail@example.com",
    "password": "newpassword"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "message": "Profile updated successfully",
    "teacher": { /* updated teacher object */ }
  }
  ```

---

## 4. TEACHER ASSIGNMENTS (REST CRUD)

### List Teacher Assignments
**GET** `/api/teacher-assignments/`
- **Description**: List all teacher assignments with optional filters
- **Auth Required**: Yes (Bearer token)
- **Query Parameters**:
  - `?teacher_id=1` - Filter by teacher
  - `?section_id=2` - Filter by section
  - `?school_year_id=1` - Filter by school year
- **Response**: `200 OK` (paginated array of assignments)
  ```json
  {
    "count": 10,
    "results": [
      {
        "assignment_id": 1,
        "teacher": 1,
        "teacher_name": "John Doe",
        "section": 2,
        "section_name": "10A",
        "subject": 5,
        "school_year": 1,
        "is_primary": true
      }
    ]
  }
  ```

### Create Teacher Assignment
**POST** `/api/teacher-assignments/`
- **Description**: Create teacher assignment (Admin only)
- **Auth Required**: Yes (Bearer token + Admin role)
- **Body**:
  ```json
  {
    "teacher": 1,
    "section": 2,
    "subject": 5,
    "school_year": 1,
    "is_primary": true
  }
  ```
- **Response**: `201 Created` (assignment object)

### Retrieve Teacher Assignment
**GET** `/api/teacher-assignments/{id}/`
- **Description**: Retrieve single teacher assignment
- **Auth Required**: Yes (Bearer token)
- **Response**: `200 OK` (single assignment object)

### Update Teacher Assignment (Full)
**PUT** `/api/teacher-assignments/{id}/`
- **Description**: Full update of assignment (Admin only)
- **Auth Required**: Yes (Bearer token + Admin role)
- **Body**: Same as Create Teacher Assignment
- **Response**: `200 OK` (updated assignment)

### Update Teacher Assignment (Partial)
**PATCH** `/api/teacher-assignments/{id}/`
- **Description**: Partial update of assignment (Admin only)
- **Auth Required**: Yes (Bearer token + Admin role)
- **Body**: Any subset of assignment fields
- **Response**: `200 OK` (updated assignment)

### Delete Teacher Assignment
**DELETE** `/api/teacher-assignments/{id}/`
- **Description**: Delete teacher assignment (Admin only)
- **Auth Required**: Yes (Bearer token + Admin role)
- **Response**: `204 No Content`

---

## 5. STUDENT MANAGEMENT (REST CRUD)

### List Students
**GET** `/api/students/`
- **Description**: List all students (paginated)
- **Auth Required**: No (AllowAny - for now)
- **Query Parameters**: `?page=1`
- **Response**: `200 OK` (paginated array)

### Create Student Enrollment
**POST** `/api/enrollments/`
- **Description**: Enroll a new student with auto-generated credentials (S001, S002, etc.)
- **Auth Required**: No (AllowAny - for now)
- **Body**:
  ```json
  {
    "first_name": "Alice",
    "last_name": "Johnson",
    "grade_level": 1,
    "school_year": 1,
    "date_of_birth": "2010-05-15",
    "email": "alice@example.com"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": 1,
    "student_id": "S001",
    "first_name": "Alice",
    "last_name": "Johnson",
    "student_login_id": "S001",
    "student_login_password": "S001",
    "grade_level": 1,
    "school_year": 1,
    "enrollment_status": "Active"
  }
  ```

### List Enrollments
**GET** `/api/enrollments/`
- **Description**: List all student enrollments (paginated)
- **Auth Required**: No (AllowAny - for now)
- **Response**: `200 OK` (paginated array)

### Retrieve Student
**GET** `/api/students/{id}/`
- **Description**: Get specific student details
- **Auth Required**: No
- **Response**: `200 OK` (student object)

### Retrieve Enrollment
**GET** `/api/enrollments/{id}/`
- **Description**: Get specific enrollment details
- **Auth Required**: No
- **Response**: `200 OK` (enrollment object)

---

## 6. PARENT MANAGEMENT (Custom Actions)

### Parent Login
**POST** `/api/parent/login/`
- **Description**: Parent login using Student ID (Student credentials) and password
- **Body**:
  ```json
  {
    "username": "S001",
    "password": "S001"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "message": "Login successful",
    "token": "abc123...",
    "student_login_id": "S001",
    "parent": {
      "parent_id": 1,
      "first_name": "Parent",
      "last_name": "Name",
      "email": "parent@example.com"
    }
  }
  ```

### Parent Logout
**POST** `/api/parent/logout/`
- **Description**: Logout and invalidate token
- **Auth Required**: Yes (Bearer token)
- **Response**: `200 OK`

### Get Parent Profile
**GET** `/api/parent/profile/`
- **Description**: Get logged-in parent's profile
- **Auth Required**: Yes (Bearer token)
- **Response**: `200 OK` (parent object)

### Get Student Info (For Parent)
**GET** `/api/parent/student-info/`
- **Description**: Get child's information (accessible to logged-in parent)
- **Auth Required**: Yes (Bearer token)
- **Response**: `200 OK` (student object)

---

## 7. GRADE LEVELS (REST CRUD)

### List Grade Levels
**GET** `/api/grade-levels/`
- **Query Parameters**: `?page=1`
- **Response**: `200 OK` (paginated array)

### Create Grade Level
**POST** `/api/grade-levels/`
- **Body**:
  ```json
  {
    "grade_name": "Grade 10",
    "abbreviation": "G10"
  }
  ```
- **Response**: `201 Created`

### Retrieve Grade Level
**GET** `/api/grade-levels/{id}/`
- **Response**: `200 OK`

### Update Grade Level
**PUT/PATCH** `/api/grade-levels/{id}/`
- **Response**: `200 OK`

### Delete Grade Level
**DELETE** `/api/grade-levels/{id}/`
- **Response**: `204 No Content`

---

## 8. SCHOOL YEARS (REST CRUD)

### List School Years
**GET** `/api/school-years/`
- **Response**: `200 OK` (paginated array)

### Create School Year
**POST** `/api/school-years/`
- **Body**:
  ```json
  {
    "year": "2024",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "is_current": true
  }
  ```
- **Response**: `201 Created`

### Get Current School Year
**GET** `/api/school-years/current/`
- **Response**: `200 OK` (single school year)

### Retrieve School Year
**GET** `/api/school-years/{id}/`
- **Response**: `200 OK`

### Update School Year
**PUT/PATCH** `/api/school-years/{id}/`
- **Response**: `200 OK`

### Delete School Year
**DELETE** `/api/school-years/{id}/`
- **Response**: `204 No Content`

---

## 9. SECTIONS (REST CRUD)

### List Sections
**GET** `/api/sections/`
- **Query Parameters**: 
  - `?page=1` - Pagination
  - `?grade_level_id=1` - Filter by grade level
- **Response**: `200 OK` (paginated array)

### Create Section
**POST** `/api/sections/`
- **Body**:
  ```json
  {
    "section_name": "10A",
    "grade_level": 1,
    "capacity": 40,
    "school_year": 1
  }
  ```
- **Response**: `201 Created`

### Get Sections by Grade Level
**GET** `/api/sections/grade-level/{id}/`
- **Description**: Get all sections for a specific grade level
- **Response**: `200 OK` (paginated array)

### Retrieve Section
**GET** `/api/sections/{id}/`
- **Response**: `200 OK`

### Update Section
**PUT/PATCH** `/api/sections/{id}/`
- **Response**: `200 OK`

### Delete Section
**DELETE** `/api/sections/{id}/`
- **Response**: `204 No Content`

---

## 10. SUBJECTS (REST CRUD)

### List Subjects
**GET** `/api/subjects/`
- **Query Parameters**: 
  - `?page=1` - Pagination
  - `?grade_level_id=1` - Filter by grade level
- **Response**: `200 OK` (paginated array)

### Create Subject
**POST** `/api/subjects/`
- **Body**:
  ```json
  {
    "subject_name": "Mathematics",
    "subject_code": "MATH",
    "description": "Advanced Mathematics",
    "grade_level": 1
  }
  ```
- **Response**: `201 Created`

### Retrieve Subject
**GET** `/api/subjects/{id}/`
- **Response**: `200 OK`

### Update Subject
**PUT/PATCH** `/api/subjects/{id}/`
- **Response**: `200 OK`

### Delete Subject
**DELETE** `/api/subjects/{id}/`
- **Response**: `204 No Content`

---

## 11. SCHEDULES (REST CRUD)

### List Schedules
**GET** `/api/schedules/`
- **Query Parameters**:
  - `?page=1` - Pagination
  - `?section_id=2` - Filter by section
  - `?day=Monday` - Filter by day
- **Response**: `200 OK` (paginated array)

### Create Schedule
**POST** `/api/schedules/`
- **Body**:
  ```json
  {
    "section": 2,
    "subject": 5,
    "day": "Monday",
    "start_time": "09:00:00",
    "end_time": "10:00:00",
    "room": "A101"
  }
  ```
- **Response**: `201 Created`

### Retrieve Schedule
**GET** `/api/schedules/{id}/`
- **Response**: `200 OK`

### Update Schedule
**PUT/PATCH** `/api/schedules/{id}/`
- **Response**: `200 OK`

### Delete Schedule
**DELETE** `/api/schedules/{id}/`
- **Response**: `204 No Content`

---

## 12. STUDENT PACE (REST CRUD + Custom Actions)

### List Student Paces
**GET** `/api/student-paces/`
- **Query Parameters**: `?page=1`
- **Response**: `200 OK` (paginated array)

### Create Student Pace
**POST** `/api/student-paces/`
- **Response**: `201 Created`

### Retrieve Student Pace
**GET** `/api/student-paces/{id}/`
- **Response**: `200 OK`

### Update Student Pace
**PUT/PATCH** `/api/student-paces/{id}/`
- **Response**: `200 OK`

### Delete Student Pace
**DELETE** `/api/student-paces/{id}/`
- **Response**: `204 No Content`

### Get Student Pace (Custom Action)
**GET** `/api/student/{student_id}/pace/`
- **Description**: Get pace for specific student
- **Response**: `200 OK`

### Get Student Warnings (Custom Action)
**GET** `/api/student/{student_id}/warnings/`
- **Description**: Get early warnings for specific student
- **Response**: `200 OK`

### List Early Warnings
**GET** `/api/early-warnings/`
- **Response**: `200 OK` (paginated array)

### Get Critical Warnings (Custom Action)
**GET** `/api/critical-warnings/`
- **Description**: Get all critical warnings across students
- **Response**: `200 OK`

---

## Authentication Headers

All authenticated endpoints require:
```
Authorization: Bearer <token>
```

Example:
```
GET /api/teachers/
Authorization: Bearer abc123def456ghi789jkl
```

---

## HTTP Status Codes

- **200 OK**: Successful GET, PUT, PATCH request
- **201 Created**: Successful POST request creating a resource
- **204 No Content**: Successful DELETE request
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Authenticated but insufficient permissions (e.g., Admin-only endpoint)
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

---

## Pagination

List endpoints support pagination:
- **Query Parameter**: `?page=1` (default: page 1)
- **Default Page Size**: 10 items
- **Response**:
  ```json
  {
    "count": 100,
    "next": "http://localhost:8000/api/resource/?page=2",
    "previous": null,
    "results": [...]
  }
  ```

---

## API Versioning

All endpoints are available under both:
- `/api/resource/` (current version)
- `/api/v1/resource/` (explicitly versioned)

Both URLs work identically and return the same response format.

---

## Swagger Documentation

Interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/swagger/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

Visit the Swagger UI to:
- View all endpoint documentation
- Test API endpoints directly
- See request/response schemas
- Understand required parameters and authentication

---

## Error Response Format

```json
{
  "field_name": ["Error message about this field"],
  "non_field_errors": ["General error message"]
}
```

Example:
```json
{
  "teacher": ["Invalid pk \"999\" - object does not exist."],
  "section": ["This field is required."]
}
```

