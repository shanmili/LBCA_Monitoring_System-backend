from django.db.models import Avg, Count, Q
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    User, Teacher, Section, Subject, Student, Guardian,
    Attendance, PaceRecord, Grade, RiskAssessment,
    Notification, ActivityLog, SchoolYear
)
from .serializers import (
    LoginSerializer, RegisterSerializer, UserSerializer,
    TeacherSerializer, SectionSerializer, SubjectSerializer,
    StudentListSerializer, StudentDetailSerializer,
    AttendanceSerializer, PaceRecordSerializer, GradeSerializer,
    RiskAssessmentSerializer, NotificationSerializer,
    ActivityLogSerializer, SchoolYearSerializer
)


# ──────────────────────────────────────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    POST /api/auth/login/
    Body: { "username": "...", "password": "..." }

    For PARENT (mobile): username = student_id (e.g. "S001"), password = student_id
    For TEACHER (web):   username = "teacher@lbca.edu", password = "teacher123"
    For ADMIN (web):     username = "admin@lbca.edu",   password = "admin123"
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']

    refresh = RefreshToken.for_user(user)
    response_data = {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
    }

    # If parent, attach linked student info
    if user.role == 'parent':
        try:
            student = user.linked_student
            response_data['student'] = {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'section': student.section.name if student.section else None,
                'grade_level': student.section.grade_level if student.section else None,
            }
        except Exception:
            response_data['student'] = None

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    POST /api/auth/register/
    Body: { "username": "...", "email": "...", "password": "...", "role": "teacher|admin|parent" }
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """POST /api/auth/logout/  Body: { "refresh": "..." }"""
    try:
        token = RefreshToken(request.data['refresh'])
        token.blacklist()
        return Response({'message': 'Logged out successfully.'})
    except Exception:
        return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """GET /api/auth/me/ — returns current user info"""
    return Response(UserSerializer(request.user).data)


# ──────────────────────────────────────────────────────────────────────────────
# DASHBOARD (Admin / Teacher)
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    GET /api/dashboard/stats/
    Query params: section (name), school_year (label), quarter (1-4)
    Returns KPI cards data for the web dashboard.
    """
    section_name    = request.query_params.get('section')
    sy_label        = request.query_params.get('school_year')

    students_qs = Student.objects.all()
    if section_name and section_name != 'All':
        students_qs = students_qs.filter(section__name=section_name)
    if sy_label:
        students_qs = students_qs.filter(school_year__year_label=sy_label)

    student_ids = students_qs.values_list('id', flat=True)

    # Latest risk assessments for these students
    risks = RiskAssessment.objects.filter(student_id__in=student_ids, is_latest=True)

    total           = students_qs.count()
    at_risk         = risks.filter(risk_level__in=['high', 'critical']).count()
    behind          = risks.filter(status='Behind').count()
    avg_attendance  = risks.aggregate(avg=Avg('attendance_percent'))['avg'] or 0
    avg_pace        = risks.aggregate(avg=Avg('pace_percent'))['avg'] or 0

    return Response({
        'total_students':          total,
        'at_risk_count':           at_risk,
        'behind_pace_count':       behind,
        'avg_attendance_percent':  round(avg_attendance, 1),
        'avg_pace_percent':        round(avg_pace, 1),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_feed(request):
    """GET /api/dashboard/activity/  — recent system activity logs"""
    logs = ActivityLog.objects.all()[:10]
    return Response(ActivityLogSerializer(logs, many=True).data)


# ──────────────────────────────────────────────────────────────────────────────
# STUDENTS
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def students_list(request):
    """
    GET  /api/students/         — list all students (filterable)
    POST /api/students/         — add a new student
    Query params for GET: section, grade_level, risk_level, search
    """
    if request.method == 'GET':
        qs = Student.objects.select_related('section', 'guardian').all()
        section     = request.query_params.get('section')
        grade       = request.query_params.get('grade_level')
        search      = request.query_params.get('search')
        if section and section != 'All':
            qs = qs.filter(section__name=section)
        if grade:
            qs = qs.filter(section__grade_level=grade)
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(student_id__icontains=search)
            )
        return Response(StudentListSerializer(qs, many=True).data)

    # POST
    serializer = StudentListSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def student_detail(request, student_id):
    """
    GET    /api/students/<student_id>/   — full student detail
    PUT    /api/students/<student_id>/   — update student
    DELETE /api/students/<student_id>/   — remove student
    """
    try:
        student = Student.objects.get(student_id=student_id)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(StudentDetailSerializer(student).data)
    if request.method == 'PUT':
        serializer = StudentDetailSerializer(student, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    if request.method == 'DELETE':
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────────────────────────────────────────
# EARLY WARNING / RISK
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def at_risk_students(request):
    """
    GET /api/risk/at-risk/
    Returns students with High or Critical risk. Query: section, grade_level
    Used by web Early Warning page and mobile Alert tab.
    """
    qs = RiskAssessment.objects.filter(
        is_latest=True,
        risk_level__in=['high', 'critical', 'moderate']
    ).select_related('student', 'student__section')

    section = request.query_params.get('section')
    grade   = request.query_params.get('grade_level')
    if section and section != 'All':
        qs = qs.filter(student__section__name=section)
    if grade:
        qs = qs.filter(student__section__grade_level=grade)

    return Response(RiskAssessmentSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_risk(request, student_id):
    """GET /api/risk/student/<student_id>/ — risk history for one student"""
    risks = RiskAssessment.objects.filter(
        student__student_id=student_id
    ).order_by('-assessed_at')
    return Response(RiskAssessmentSerializer(risks, many=True).data)


# ──────────────────────────────────────────────────────────────────────────────
# PACE
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def pace_records(request):
    """
    GET  /api/pace/          — list pace records (filterable by student, subject, quarter, section)
    POST /api/pace/          — add/update a pace record
    """
    if request.method == 'GET':
        qs = PaceRecord.objects.select_related('student', 'subject').all()
        student_id  = request.query_params.get('student_id')
        subject     = request.query_params.get('subject')
        quarter     = request.query_params.get('quarter')
        section     = request.query_params.get('section')
        if student_id:
            qs = qs.filter(student__student_id=student_id)
        if subject:
            qs = qs.filter(subject__name=subject)
        if quarter:
            qs = qs.filter(quarter=quarter)
        if section:
            qs = qs.filter(student__section__name=section)
        return Response(PaceRecordSerializer(qs, many=True).data)

    serializer = PaceRecordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(recorded_by=request.user.teacher_profile if hasattr(request.user, 'teacher_profile') else None)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# ──────────────────────────────────────────────────────────────────────────────
# GRADES
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def grades_list(request):
    """
    GET  /api/grades/    — list grades (filter by student_id, quarter)
    POST /api/grades/    — create/update a grade
    """
    if request.method == 'GET':
        qs = Grade.objects.select_related('student', 'subject').all()
        student_id  = request.query_params.get('student_id')
        quarter     = request.query_params.get('quarter')
        if student_id:
            qs = qs.filter(student__student_id=student_id)
        if quarter:
            qs = qs.filter(quarter=quarter)
        return Response(GradeSerializer(qs, many=True).data)

    serializer = GradeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# ──────────────────────────────────────────────────────────────────────────────
# ATTENDANCE
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def attendance_list(request):
    """
    GET  /api/attendance/    — filter by student_id, date, month
    POST /api/attendance/    — record attendance
    """
    if request.method == 'GET':
        qs = Attendance.objects.select_related('student').all()
        student_id  = request.query_params.get('student_id')
        month       = request.query_params.get('month')   # e.g. "2026-01"
        if student_id:
            qs = qs.filter(student__student_id=student_id)
        if month:
            qs = qs.filter(date__startswith=month)
        return Response(AttendanceSerializer(qs, many=True).data)

    serializer = AttendanceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# ──────────────────────────────────────────────────────────────────────────────
# TEACHERS
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def teachers_list(request):
    """
    GET  /api/teachers/    — list all teachers
    POST /api/teachers/    — create a teacher
    """
    if request.method == 'GET':
        teachers = Teacher.objects.all()
        return Response(TeacherSerializer(teachers, many=True).data)

    serializer = TeacherSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def teacher_detail(request, pk):
    """GET/PUT/DELETE /api/teachers/<pk>/"""
    try:
        teacher = Teacher.objects.get(pk=pk)
    except Teacher.DoesNotExist:
        return Response({'error': 'Teacher not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(TeacherSerializer(teacher).data)
    if request.method == 'PUT':
        serializer = TeacherSerializer(teacher, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    teacher.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────────────────────────────────────────
# SECTIONS & SUBJECTS
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sections_list(request):
    """GET /api/sections/"""
    sections = Section.objects.select_related('school_year', 'adviser').all()
    return Response(SectionSerializer(sections, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subjects_list(request):
    """GET /api/subjects/"""
    subjects = Subject.objects.all()
    return Response(SubjectSerializer(subjects, many=True).data)


# ──────────────────────────────────────────────────────────────────────────────
# NOTIFICATIONS (Mobile - Parent)
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_list(request):
    """GET /api/notifications/  — returns notifications for logged-in user"""
    notifs = Notification.objects.filter(recipient=request.user)
    return Response(NotificationSerializer(notifs, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    """POST /api/notifications/<pk>/read/"""
    try:
        notif = Notification.objects.get(pk=pk, recipient=request.user)
        notif.is_read = True
        notif.save()
        return Response({'message': 'Marked as read.'})
    except Notification.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """POST /api/notifications/mark-all-read/"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read.'})


# ──────────────────────────────────────────────────────────────────────────────
# PARENT / MOBILE — My Student
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_student(request):
    """
    GET /api/parent/my-student/
    Returns the full profile of the student linked to the logged-in parent.
    """
    if request.user.role != 'parent':
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    try:
        student = request.user.linked_student
        return Response(StudentDetailSerializer(student).data)
    except Exception:
        return Response({'error': 'No student linked to this account.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_student_grades(request):
    """GET /api/parent/grades/  — quarterly grades for logged-in parent's child"""
    if request.user.role != 'parent':
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    try:
        student = request.user.linked_student
        quarter = request.query_params.get('quarter')
        qs = Grade.objects.filter(student=student).select_related('subject')
        if quarter:
            qs = qs.filter(quarter=quarter)
        return Response(GradeSerializer(qs, many=True).data)
    except Exception:
        return Response({'error': 'No student linked.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_student_attendance(request):
    """GET /api/parent/attendance/  — attendance records for logged-in parent's child"""
    if request.user.role != 'parent':
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    try:
        student = request.user.linked_student
        month = request.query_params.get('month')
        qs = Attendance.objects.filter(student=student)
        if month:
            qs = qs.filter(date__startswith=month)
        return Response(AttendanceSerializer(qs, many=True).data)
    except Exception:
        return Response({'error': 'No student linked.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_student_pace(request):
    """GET /api/parent/pace/  — PACE records for logged-in parent's child"""
    if request.user.role != 'parent':
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    try:
        student = request.user.linked_student
        quarter = request.query_params.get('quarter')
        qs = PaceRecord.objects.filter(student=student).select_related('subject')
        if quarter:
            qs = qs.filter(quarter=quarter)
        return Response(PaceRecordSerializer(qs, many=True).data)
    except Exception:
        return Response({'error': 'No student linked.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_student_risk(request):
    """GET /api/parent/risk/  — latest risk assessment for logged-in parent's child"""
    if request.user.role != 'parent':
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    try:
        student = request.user.linked_student
        risk = RiskAssessment.objects.filter(student=student, is_latest=True).first()
        if not risk:
            return Response({'message': 'No risk data available.'})
        return Response(RiskAssessmentSerializer(risk).data)
    except Exception:
        return Response({'error': 'No student linked.'}, status=status.HTTP_404_NOT_FOUND)
