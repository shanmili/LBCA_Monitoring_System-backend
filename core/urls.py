from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────────
    path('auth/login/',             views.login_view,               name='login'),
    path('auth/register/',          views.register_view,            name='register'),
    path('auth/logout/',            views.logout_view,              name='logout'),
    path('auth/me/',                views.me_view,                  name='me'),

    # ── Dashboard (web) ───────────────────────────────────────────────────────
    path('dashboard/stats/',        views.dashboard_stats,          name='dashboard-stats'),
    path('dashboard/activity/',     views.activity_feed,            name='activity-feed'),

    # ── Students ──────────────────────────────────────────────────────────────
    path('students/',               views.students_list,            name='students-list'),
    path('students/<str:student_id>/', views.student_detail,        name='student-detail'),

    # ── Risk / Early Warning ──────────────────────────────────────────────────
    path('risk/at-risk/',           views.at_risk_students,         name='at-risk'),
    path('risk/student/<str:student_id>/', views.student_risk,      name='student-risk'),

    # ── PACE ──────────────────────────────────────────────────────────────────
    path('pace/',                   views.pace_records,             name='pace-records'),

    # ── Grades ────────────────────────────────────────────────────────────────
    path('grades/',                 views.grades_list,              name='grades-list'),

    # ── Attendance ────────────────────────────────────────────────────────────
    path('attendance/',             views.attendance_list,          name='attendance-list'),

    # ── Teachers ──────────────────────────────────────────────────────────────
    path('teachers/',               views.teachers_list,            name='teachers-list'),
    path('teachers/<int:pk>/',      views.teacher_detail,           name='teacher-detail'),

    # ── Sections & Subjects ───────────────────────────────────────────────────
    path('sections/',               views.sections_list,            name='sections-list'),
    path('subjects/',               views.subjects_list,            name='subjects-list'),

    # ── Notifications ─────────────────────────────────────────────────────────
    path('notifications/',                          views.notifications_list,           name='notifs'),
    path('notifications/<int:pk>/read/',            views.mark_notification_read,       name='notif-read'),
    path('notifications/mark-all-read/',            views.mark_all_notifications_read,  name='notifs-read-all'),

    # ── Parent (mobile) ───────────────────────────────────────────────────────
    path('parent/my-student/',      views.my_student,               name='my-student'),
    path('parent/grades/',          views.my_student_grades,        name='my-grades'),
    path('parent/attendance/',      views.my_student_attendance,    name='my-attendance'),
    path('parent/pace/',            views.my_student_pace,          name='my-pace'),
    path('parent/risk/',            views.my_student_risk,          name='my-risk'),
]
