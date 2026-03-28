from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# ─── Custom User Manager ─────────────────────────────────────────────────────
class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)


# ─── User ─────────────────────────────────────────────────────────────────────
# Web roles: teacher, admin
# Mobile role: parent (logs in with student_id as username AND password)
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
    ]

    username    = models.CharField(max_length=50, unique=True)  # student_id for parents
    email       = models.EmailField(blank=True, null=True)
    role        = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    objects = UserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f'{self.username} ({self.role})'


# ─── School Year ─────────────────────────────────────────────────────────────
class SchoolYear(models.Model):
    year_label  = models.CharField(max_length=20, unique=True)  # e.g. "2025-2026"
    is_current  = models.BooleanField(default=False)

    class Meta:
        db_table = 'school_years'

    def __str__(self):
        return self.year_label


# ─── Teacher ─────────────────────────────────────────────────────────────────
class Teacher(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    middle_name     = models.CharField(max_length=50, blank=True, null=True)
    email           = models.EmailField(unique=True)
    employee_id     = models.CharField(max_length=20, unique=True)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'teachers'

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'


# ─── Section ─────────────────────────────────────────────────────────────────
class Section(models.Model):
    name        = models.CharField(max_length=50)       # e.g. "Section A", "Faith"
    grade_level = models.CharField(max_length=20)       # e.g. "Grade 10"
    adviser     = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)

    class Meta:
        db_table = 'sections'
        unique_together = ('name', 'grade_level', 'school_year')

    def __str__(self):
        return f'{self.grade_level} - {self.name}'


# ─── Subject ─────────────────────────────────────────────────────────────────
class Subject(models.Model):
    name        = models.CharField(max_length=100)   # Math, English, Science, etc.
    color_hex   = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'subjects'

    def __str__(self):
        return self.name


# ─── Teacher Subject Assignment ───────────────────────────────────────────────
class TeacherSubjectAssignment(models.Model):
    teacher         = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject         = models.ForeignKey(Subject, on_delete=models.CASCADE)
    section         = models.ForeignKey(Section, on_delete=models.CASCADE)
    consult_hours   = models.CharField(max_length=50, blank=True, null=True)  # e.g. "7:30 – 8:30 AM"

    class Meta:
        db_table = 'teacher_subject_assignments'
        unique_together = ('teacher', 'subject', 'section')


# ─── Teacher Availability ─────────────────────────────────────────────────────
class TeacherAvailability(models.Model):
    DAY_CHOICES = [
        ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'), ('Fri', 'Friday'),
    ]
    assignment  = models.ForeignKey(TeacherSubjectAssignment, on_delete=models.CASCADE)
    day         = models.CharField(max_length=3, choices=DAY_CHOICES)
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = 'teacher_availability'
        unique_together = ('assignment', 'day')


# ─── Student ─────────────────────────────────────────────────────────────────
class Student(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]

    student_id      = models.CharField(max_length=20, unique=True)  # e.g. "S001"
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    middle_name     = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth   = models.DateField(null=True, blank=True)
    gender          = models.CharField(max_length=10, choices=GENDER_CHOICES)
    address         = models.TextField(blank=True, null=True)
    section         = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    school_year     = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)

    # The parent/guardian user linked to this student (for mobile login)
    parent_user     = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='linked_student'
    )

    class Meta:
        db_table = 'students'

    def __str__(self):
        return f'{self.student_id} - {self.last_name}, {self.first_name}'


# ─── Guardian / Parent Info ───────────────────────────────────────────────────
class Guardian(models.Model):
    RELATIONSHIP_CHOICES = [
        ('Father', 'Father'), ('Mother', 'Mother'), ('Guardian', 'Guardian'),
    ]
    student         = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='guardian')
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    middle_name     = models.CharField(max_length=50, blank=True, null=True)
    contact_number  = models.CharField(max_length=20)
    relationship    = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)

    class Meta:
        db_table = 'guardians'

    def __str__(self):
        return f'{self.last_name} (Guardian of {self.student.student_id})'


# ─── Attendance ───────────────────────────────────────────────────────────────
class Attendance(models.Model):
    STATUS_CHOICES = [('present', 'Present'), ('late', 'Late'), ('absent', 'Absent')]

    student     = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date        = models.DateField()
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES)
    recorded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'attendance'
        unique_together = ('student', 'date')

    def __str__(self):
        return f'{self.student.student_id} - {self.date} - {self.status}'


# ─── PACE (student workbook completion per subject) ───────────────────────────
class PaceRecord(models.Model):
    student     = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='pace_records')
    subject     = models.ForeignKey(Subject, on_delete=models.CASCADE)
    quarter     = models.PositiveSmallIntegerField()   # 1, 2, 3, or 4
    pace_number = models.PositiveSmallIntegerField()   # PACE booklet number
    completed   = models.BooleanField(default=False)
    test_score  = models.FloatField(null=True, blank=True)
    recorded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pace_records'
        unique_together = ('student', 'subject', 'quarter', 'pace_number')

    def __str__(self):
        return f'{self.student.student_id} - {self.subject.name} - Q{self.quarter} PACE#{self.pace_number}'


# ─── Grades (quarterly) ───────────────────────────────────────────────────────
class Grade(models.Model):
    student     = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject     = models.ForeignKey(Subject, on_delete=models.CASCADE)
    quarter     = models.PositiveSmallIntegerField()
    grade_value = models.FloatField(null=True, blank=True)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)
    recorded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'grades'
        unique_together = ('student', 'subject', 'quarter', 'school_year')

    def __str__(self):
        return f'{self.student.student_id} - {self.subject.name} Q{self.quarter}: {self.grade_value}'


# ─── Risk Assessment ──────────────────────────────────────────────────────────
class RiskAssessment(models.Model):
    RISK_CHOICES = [
        ('low', 'Low'), ('moderate', 'Moderate'),
        ('high', 'High'), ('critical', 'Critical'),
    ]
    TREND_CHOICES = [
        ('improving', 'Improving'), ('stable', 'Stable'), ('declining', 'Declining'),
    ]
    STATUS_CHOICES = [
        ('On Track', 'On Track'), ('Behind', 'Behind'),
        ('At Risk', 'At Risk'), ('Critical', 'Critical'),
    ]

    student             = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='risk_assessments')
    assessed_at         = models.DateTimeField(auto_now_add=True)
    risk_level          = models.CharField(max_length=10, choices=RISK_CHOICES)
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES)
    pace_percent        = models.FloatField()
    attendance_percent  = models.FloatField()
    trend               = models.CharField(max_length=10, choices=TREND_CHOICES, default='stable')
    primary_factor      = models.CharField(max_length=200, blank=True, null=True)
    secondary_factor    = models.CharField(max_length=200, blank=True, null=True)
    suggested_action    = models.CharField(max_length=200, blank=True, null=True)
    paces_behind        = models.IntegerField(default=0)
    is_latest           = models.BooleanField(default=True)

    class Meta:
        db_table = 'risk_assessments'

    def __str__(self):
        return f'{self.student.student_id} - {self.risk_level} ({self.assessed_at.date()})'


# ─── Notification ─────────────────────────────────────────────────────────────
class Notification(models.Model):
    TYPE_CHOICES = [
        ('grade', 'Grade'), ('alert', 'Alert'),
        ('announcement', 'Announcement'), ('schedule', 'Schedule'),
    ]

    recipient       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title           = models.CharField(max_length=200)
    body            = models.TextField()
    is_read         = models.BooleanField(default=False)
    route           = models.CharField(max_length=50, blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient.username} - {self.title}'


# ─── Activity Log (for admin dashboard activity feed) ─────────────────────────
class ActivityLog(models.Model):
    TYPE_CHOICES = [
        ('alert', 'Alert'), ('pace', 'PACE'),
        ('attendance', 'Attendance'), ('risk', 'Risk'), ('system', 'System'),
    ]

    log_type    = models.CharField(max_length=15, choices=TYPE_CHOICES)
    text        = models.CharField(max_length=300)
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.log_type}] {self.text}'
