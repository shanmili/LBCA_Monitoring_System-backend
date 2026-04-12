import json
import re
from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from grade_levels.models import GradeLevel
from school_years.models import SchoolYear
from sections.models import Section
from student_pace.models import EarlyWarning, StudentPace
from subjects.models import Subject
from students.models import Student, StudentEnrollment
from teachers.models import Teacher

try:
    from parents.models import Parent
except Exception:  # pragma: no cover
    Parent = None


def _pick_relationship(value: str) -> str:
    value = (value or '').strip().lower()
    if value in {'parent', 'father', 'mother'}:
        return 'Parent'
    if value in {'guardian'}:
        return 'Guardian'
    return 'Other'


def _pick_risk_level(value: str) -> str:
    value = (value or '').strip().lower()
    if value == 'high':
        return 'high'
    if value == 'medium':
        return 'moderate'
    if value == 'low':
        return 'low'
    return 'moderate'


def _pick_status(value: str) -> str:
    value = (value or '').strip().lower()
    if value == 'behind':
        return 'At Risk'
    if value == 'at risk':
        return 'Critical'
    return 'On Track'


def _grade_from_text(grade_text: str) -> tuple[str, str]:
    match = re.search(r"(\d+)", grade_text or '')
    num = match.group(1) if match else '10'
    level = f'Grade {num}'
    suffix = {"1": "First", "2": "Second", "3": "Third"}.get(num, f'{num}th')
    return level, f'{suffix} Grade'


def _section_code(grade_level: str, section_name: str) -> str:
    match = re.search(r"(\d+)", grade_level or '')
    grade_num = match.group(1) if match else '10'
    suffix = (section_name or 'Section A').split()[-1]
    return f'{grade_num}-{suffix}'


def _subject_code(grade_level: str, subject_name: str) -> str:
    match = re.search(r"(\d+)", grade_level or '')
    grade_num = match.group(1) if match else '10'
    normalized = re.sub(r'[^A-Za-z0-9]+', '', subject_name or 'GENERAL').upper()
    short_name = normalized[:14] if normalized else 'GENERAL'
    return f'G{grade_num}-{short_name}'


class Command(BaseCommand):
    help = 'Import frontend mock data JSON into Django models (teachers, students, enrollments, pace, warnings).'

    def add_arguments(self, parser):
        parser.add_argument('--file', required=True, help='Path to JSON file with studentsData/teachersData.')
        parser.add_argument('--school-year', default='2025-2026', help='School year label to use for enrollments.')

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = options['file']
        school_year_label = options['school_year']

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                payload = json.load(f)
        except FileNotFoundError as exc:
            raise CommandError(f'File not found: {file_path}') from exc
        except json.JSONDecodeError as exc:
            raise CommandError(f'Invalid JSON: {exc}') from exc

        students_data = payload.get('studentsData', [])
        teachers_data = payload.get('teachersData', [])

        if not students_data and not teachers_data:
            raise CommandError('JSON must include at least one of: studentsData, teachersData')

        school_year, _ = SchoolYear.objects.get_or_create(
            year=school_year_label,
            defaults={
                'is_current': True,
                'start_date': date(2025, 6, 1),
                'end_date': date(2026, 3, 31),
            },
        )

        created_teachers = 0
        created_students = 0
        created_enrollments = 0
        created_subjects = 0
        created_paces = 0
        created_warnings = 0

        for t in teachers_data:
            username = (t.get('username') or '').strip()
            if not username:
                continue
            password = t.get('password') or username
            status = 'Inactive' if (t.get('status') or '').lower() == 'inactive' else 'Active'

            user, user_created = User.objects.get_or_create(username=username)
            if user_created:
                user.set_password(password)
                user.save()

            teacher, teacher_created = Teacher.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': t.get('firstName') or '',
                    'middle_name': t.get('middleName') or '',
                    'last_name': t.get('lastName') or '',
                    'contact_number': t.get('contactNumber') or '',
                    'email': t.get('email') or f'{username}@example.local',
                    'role': 'Teacher',
                    'status': status,
                    'is_first_login': False,
                },
            )
            if teacher_created:
                created_teachers += 1

        for s in students_data:
            sid = (s.get('id') or '').strip()
            if not sid:
                continue

            user, user_created = User.objects.get_or_create(username=sid)
            if user_created:
                # Parent login design uses student id as password by default.
                user.set_password(sid)
                user.save()

            relationship = _pick_relationship(s.get('guardianRelationship'))
            student, student_created = Student.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': s.get('firstName') or '',
                    'middle_name': s.get('middleName') or '',
                    'last_name': s.get('lastName') or '',
                    'birth_date': s.get('dateOfBirth') or '2008-01-01',
                    'gender': s.get('gender') or 'Male',
                    'address': s.get('address') or '',
                    'guardian_first_name': s.get('guardianFirstName') or '',
                    'guardian_mid_name': s.get('guardianMiddleName') or '',
                    'guardian_last_name': s.get('guardianLastName') or '',
                    'guardian_contact': s.get('guardianContact') or '',
                    'relationship': relationship,
                },
            )
            if student_created:
                created_students += 1

            grade_level_text = s.get('gradeLevel') or 'Grade 10'
            level, grade_name = _grade_from_text(grade_level_text)
            grade_level, _ = GradeLevel.objects.get_or_create(level=level, defaults={'name': grade_name})

            section_name = s.get('section') or 'Section A'
            sec_code = _section_code(level, section_name)
            section, _ = Section.objects.get_or_create(
                section_code=sec_code,
                defaults={'name': section_name, 'grade_level': grade_level},
            )

            enrollment, enroll_created = StudentEnrollment.objects.get_or_create(
                student=student,
                grade_level=grade_level,
                section=section,
                school_year=school_year,
                defaults={'is_active': True},
            )
            if enroll_created:
                created_enrollments += 1

            # Keep the Subject master list synced with mock data subjects per grade level.
            for subj in s.get('subjects', []):
                subject_name = (subj.get('name') or 'General').strip() or 'General'
                subject_code = _subject_code(level, subject_name)
                _, subject_created = Subject.objects.get_or_create(
                    subject_code=subject_code,
                    defaults={
                        'grade_level': grade_level,
                        'subject_name': subject_name,
                    },
                )
                if subject_created:
                    created_subjects += 1

            # Build pace rows from subjects list when provided.
            for subj in s.get('subjects', []):
                total = subj.get('total') or 0
                completed = subj.get('completed') or 0
                pace_percent = round((completed / total) * 100, 2) if total else float(s.get('pacePercent') or 0)
                paces_behind = max(0, int((100 - pace_percent) // 10))

                _, pace_created = StudentPace.objects.get_or_create(
                    student=student,
                    enrollment=enrollment,
                    subject=subj.get('name') or 'General',
                    defaults={
                        'pace_percent': pace_percent,
                        'paces_behind': paces_behind,
                    },
                )
                if pace_created:
                    created_paces += 1

                risk_value = _pick_risk_level(s.get('riskLevel'))
                if risk_value in {'high', 'moderate'}:
                    _, warning_created = EarlyWarning.objects.get_or_create(
                        student=student,
                        enrollment=enrollment,
                        subject=subj.get('name') or 'General',
                        defaults={
                            'teacher': 'Unassigned',
                            'risk_level': risk_value,
                            'paces_behind': paces_behind,
                            'pace_percent': float(s.get('pacePercent') or pace_percent),
                            'attendance': float(s.get('attendance') or 0),
                            'status': _pick_status(s.get('status')),
                            'trend': 'stable',
                            'last_activity': 'Imported',
                        },
                    )
                    if warning_created:
                        created_warnings += 1

            # Keep parent table aligned with student guardian data when app exists.
            if Parent is not None:
                Parent.objects.get_or_create(
                    student=student,
                    defaults={
                        'first_name': s.get('guardianFirstName') or 'Guardian',
                        'middle_name': s.get('guardianMiddleName') or '',
                        'last_name': s.get('guardianLastName') or 'Unknown',
                        'email': f'{sid.lower()}@parent.local',
                        'phone': s.get('guardianContact') or '',
                        'relationship': relationship,
                    },
                )

        self.stdout.write(self.style.SUCCESS('Import complete.'))
        self.stdout.write(
            f'Teachers created: {created_teachers} | Students created: {created_students} | '
            f'Enrollments created: {created_enrollments} | Subjects created: {created_subjects} | '
            f'Pace rows created: {created_paces} | '
            f'Early warnings created: {created_warnings}'
        )
