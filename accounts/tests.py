from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import User, Member


class UserViewSetTestCase(APITestCase):
    """Test cases for UserViewSet"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create a test user
        self.test_user = User.objects.create_user(
            login='testuser',
            email='test@example.com',
            name='Test User',
            role='Librarian',
            password='testpass123',
            is_staff_member=True
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            login='admin',
            email='admin@example.com',
            name='Admin User',
            role='Administrator',
            password='adminpass123',
            is_staff_member=True,
            is_staff=True,
            is_superuser=True
        )

    def test_login_success(self):
        """Test successful login"""
        url = reverse('user-login')
        data = {
            'login': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['login'], 'testuser')

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('user-login')
        data = {
            'login': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_login_missing_fields(self):
        """Test login with missing fields"""
        url = reverse('user-login')
        data = {
            'login': 'testuser'
            # Missing password
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user(self):
        """Test login with inactive user"""
        # Create inactive user
        inactive_user = User.objects.create_user(
            login='inactive',
            email='inactive@example.com',
            name='Inactive User',
            role='Librarian',
            password='testpass123',
            is_staff_member=True,
            is_active=False
        )
        
        url = reverse('user-login')
        data = {
            'login': 'inactive',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_non_staff_user(self):
        """Test login with non-staff user"""
        # Create non-staff user
        non_staff_user = User.objects.create_user(
            login='nonstaff',
            email='nonstaff@example.com',
            name='Non Staff User',
            role='Member',
            password='testpass123',
            is_staff_member=False
        )
        
        url = reverse('user-login')
        data = {
            'login': 'nonstaff',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_authenticated(self):
        """Test getting profile when authenticated"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('user-profile')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['login'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_profile_unauthenticated(self):
        """Test getting profile when not authenticated"""
        url = reverse('user-profile')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_authenticated(self):
        """Test creating a new user when authenticated"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-list')
        data = {
            'login': 'newuser',
            'email': 'newuser@example.com',
            'name': 'New User',
            'role': 'Assistant',
            'password': 'newpass123',
            'is_staff_member': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['login'], 'newuser')
        self.assertTrue(User.objects.filter(login='newuser').exists())

    def test_create_user_unauthenticated(self):
        """Test creating a user when not authenticated"""
        url = reverse('user-list')
        data = {
            'login': 'newuser',
            'email': 'newuser@example.com',
            'name': 'New User',
            'role': 'Assistant',
            'password': 'newpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_authenticated(self):
        """Test listing users when authenticated"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('user-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)  # At least test_user and admin_user

    def test_list_users_unauthenticated(self):
        """Test listing users when not authenticated"""
        url = reverse('user-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_authenticated(self):
        """Test retrieving a specific user when authenticated"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('user-detail', kwargs={'pk': self.test_user.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['login'], 'testuser')

    def test_update_user_authenticated(self):
        """Test updating a user when authenticated"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-detail', kwargs={'pk': self.test_user.pk})
        data = {
            'login': 'testuser',
            'email': 'test@example.com',
            'name': 'Updated Test User',
            'role': 'Senior Librarian',
            'is_staff_member': True
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Test User')

    def test_delete_user_authenticated(self):
        """Test deleting a user when authenticated"""
        # Create user to delete
        user_to_delete = User.objects.create_user(
            login='todelete',
            email='delete@example.com',
            name='To Delete',
            role='Temp',
            password='temp123',
            is_staff_member=True
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-detail', kwargs={'pk': user_to_delete.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=user_to_delete.pk).exists())


class MemberViewSetTestCase(APITestCase):
    """Test cases for MemberViewSet"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create a test user for authentication
        self.test_user = User.objects.create_user(
            login='testuser',
            email='test@example.com',
            name='Test User',
            role='Librarian',
            password='testpass123',
            is_staff_member=True
        )
        
        # Create test members
        self.member1 = Member.objects.create(
            name='John Doe',
            cpf='12345678901',
            email='john.doe@example.com',
            phone='1234567890'
        )
        
        self.member2 = Member.objects.create(
            name='Jane Smith',
            cpf='98765432109',
            email='jane.smith@example.com',
            phone='0987654321'
        )

    def test_list_members_authenticated(self):
        """Test listing members when authenticated"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_members_unauthenticated(self):
        """Test listing members when not authenticated"""
        url = reverse('member-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_member_authenticated(self):
        """Test creating a new member when authenticated"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-list')
        data = {
            'name': 'New Member',
            'cpf': '11111111111',
            'email': 'new@example.com',
            'phone': '1111111111'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Member')
        self.assertTrue(Member.objects.filter(cpf='11111111111').exists())

    def test_create_member_unauthenticated(self):
        """Test creating a member when not authenticated"""
        url = reverse('member-list')
        data = {
            'name': 'New Member',
            'cpf': '11111111111',
            'email': 'new@example.com'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_member_duplicate_cpf(self):
        """Test creating a member with duplicate CPF"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-list')
        data = {
            'name': 'Duplicate CPF',
            'cpf': '12345678901',  # Same as member1
            'email': 'duplicate@example.com'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cpf', response.data)

    def test_create_member_duplicate_email(self):
        """Test creating a member with duplicate email"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-list')
        data = {
            'name': 'Duplicate Email',
            'cpf': '22222222222',
            'email': 'john.doe@example.com'  # Same as member1
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_create_member_invalid_cpf(self):
        """Test creating a member with invalid CPF"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-list')
        data = {
            'name': 'Invalid CPF',
            'cpf': '123',  # Too short
            'email': 'invalid@example.com'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cpf', response.data)

    def test_retrieve_member_authenticated(self):
        """Test retrieving a specific member when authenticated"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-detail', kwargs={'pk': self.member1.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Doe')
        self.assertEqual(response.data['cpf'], '12345678901')

    def test_update_member_authenticated(self):
        """Test updating a member when authenticated"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-detail', kwargs={'pk': self.member1.pk})
        data = {
            'name': 'John Updated',
            'cpf': '12345678901',
            'email': 'john.updated@example.com',
            'phone': '9999999999'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Updated')
        self.assertEqual(response.data['phone'], '9999999999')

    def test_partial_update_member_authenticated(self):
        """Test partially updating a member when authenticated"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-detail', kwargs={'pk': self.member1.pk})
        data = {
            'phone': '8888888888'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone'], '8888888888')
        self.assertEqual(response.data['name'], 'John Doe')  # Should remain unchanged

    def test_delete_member_authenticated(self):
        """Test deleting a member when authenticated"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-detail', kwargs={'pk': self.member2.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Member.objects.filter(pk=self.member2.pk).exists())

    def test_search_members_by_name(self):
        """Test searching members by name"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-list')
        
        response = self.client.get(url, {'search': 'John'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'John Doe')

    def test_search_members_by_email(self):
        """Test searching members by email"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-list')
        
        response = self.client.get(url, {'search': 'jane.smith'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], 'jane.smith@example.com')

    def test_search_members_by_cpf(self):
        """Test searching members by CPF"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-list')
        
        response = self.client.get(url, {'search': '987654'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['cpf'], '98765432109')

    def test_search_members_no_results(self):
        """Test searching members with no matching results"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-list')
        
        response = self.client.get(url, {'search': 'nonexistent'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_members_ordered_by_name(self):
        """Test that members are ordered by name"""
        self.client.force_authenticate(user=self.test_user)
        url = reverse('member-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [member['name'] for member in response.data['results']]
        self.assertEqual(names, sorted(names))  # Should be in alphabetical order


class UserModelTestCase(TestCase):
    """Test cases for User model"""
    
    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(
            login='testuser',
            email='test@example.com',
            name='Test User',
            role='Librarian',
            password='testpass123'
        )
        
        self.assertEqual(user.login, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff_member)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            login='admin',
            email='admin@example.com',
            name='Admin User',
            password='adminpass123'
        )
        
        self.assertEqual(user.login, 'admin')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff_member)
        self.assertEqual(user.role, 'Administrator')

    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            login='testuser',
            email='test@example.com',
            name='Test User',
            role='Librarian',
            password='testpass123'
        )
        
        expected_str = "Test User - Librarian"
        self.assertEqual(str(user), expected_str)


class MemberModelTestCase(TestCase):
    """Test cases for Member model"""
    
    def test_create_member(self):
        """Test creating a member"""
        member = Member.objects.create(
            name='John Doe',
            cpf='12345678901',
            email='john@example.com',
            phone='1234567890'
        )
        
        self.assertEqual(member.name, 'John Doe')
        self.assertEqual(member.cpf, '12345678901')
        self.assertEqual(member.email, 'john@example.com')
        self.assertEqual(member.phone, '1234567890')

    def test_member_str_representation(self):
        """Test member string representation"""
        member = Member.objects.create(
            name='John Doe',
            cpf='12345678901',
            email='john@example.com'
        )
        
        expected_str = "John Doe - john@example.com"
        self.assertEqual(str(member), expected_str)

    def test_member_unique_cpf(self):
        """Test that CPF must be unique"""
        Member.objects.create(
            name='John Doe',
            cpf='12345678901',
            email='john@example.com'
        )
        
        with self.assertRaises(Exception):
            Member.objects.create(
                name='Jane Doe',
                cpf='12345678901',  # Duplicate CPF
                email='jane@example.com'
            )

    def test_member_unique_email(self):
        """Test that email must be unique"""
        Member.objects.create(
            name='John Doe',
            cpf='12345678901',
            email='john@example.com'
        )
        
        with self.assertRaises(Exception):
            Member.objects.create(
                name='Jane Doe',
                cpf='98765432109',
                email='john@example.com'  # Duplicate email
            )
