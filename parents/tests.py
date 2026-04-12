from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from students.models import Student
from .models import Parent


class ParentLoginTestCase(APITestCase):
    def setUp(self):
        # Create a user (student)
        self.user = User.objects.create_user(username='STU001', password='STU001')
        
        # Create a student
        self.student = Student.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            birth_date='2010-01-15',
            gender='Male',
            address='123 Main St',
            guardian_first_name='Jane',
            guardian_last_name='Doe',
            guardian_contact='555-1234',
            relationship='Parent'
        )
        
        # Create a parent
        self.parent = Parent.objects.create(
            student=self.student,
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            phone='555-1234',
            relationship='Parent'
        )

    def test_parent_login_success(self):
        response = self.client.post('/api/parent/login/', {
            'username': 'STU001',
            'password': 'STU001'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_parent_login_invalid_credentials(self):
        response = self.client.post('/api/parent/login/', {
            'username': 'STU001',
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, 401)

    def test_parent_login_missing_fields(self):
        response = self.client.post('/api/parent/login/', {
            'username': 'STU001'
        })
        self.assertEqual(response.status_code, 400)
