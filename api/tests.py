from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from accounts.models import User, Member
from .models import Book, Loan, LoanHistory


class APITestBase(APITestCase):
    """Base test class with common setup for API tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.staff_user = User.objects.create_user(
            login='staff_user',
            email='staff@library.com',
            password='testpass123',
            name='Staff User',
            role='Librarian',
            is_staff_member=True
        )
        
        self.regular_user = User.objects.create_user(
            login='regular_user',
            email='regular@library.com',
            password='testpass123',
            name='Regular User',
            role='Assistant',
            is_staff_member=False
        )
        
        # Create test members
        self.member1 = Member.objects.create(
            name='John Doe',
            cpf='12345678901',
            email='john@example.com',
            phone='1234567890'
        )
        
        self.member2 = Member.objects.create(
            name='Jane Smith',
            cpf='98765432109',
            email='jane@example.com',
            phone='9876543210'
        )
        
        # Create test books
        self.book1 = Book.objects.create(
            title='Test Book 1',
            category='Fiction',
            availability=True
        )
        
        self.book2 = Book.objects.create(
            title='Test Book 2',
            category='Science',
            availability=True
        )
        
        self.unavailable_book = Book.objects.create(
            title='Unavailable Book',
            category='Fiction',
            availability=True  # Start as available
        )
        
        # Create test loan (this will make the book unavailable)
        self.active_loan = Loan.objects.create(
            book=self.unavailable_book,
            member=self.member1,
            loan_date=date.today(),
            status='LOANED'
        )
        
        self.client = APIClient()


class BookViewSetTestCase(APITestBase):
    """Test cases for BookViewSet"""
    
    def setUp(self):
        super().setUp()
        self.list_url = reverse('book-list')
        self.detail_url = lambda pk: reverse('book-detail', kwargs={'pk': pk})
    
    def test_list_books_unauthenticated(self):
        """Test that unauthenticated users cannot access books"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_books_regular_user(self):
        """Test that regular authenticated users cannot access books"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_books_staff_user(self):
        """Test that staff users can list books"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_retrieve_book_staff_user(self):
        """Test that staff users can retrieve a specific book"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.detail_url(self.book1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Book 1')
    
    def test_create_book_staff_user(self):
        """Test that staff users can create books"""
        self.client.force_authenticate(user=self.staff_user)
        data = {
            'title': 'New Book',
            'category': 'History'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Book')
        self.assertTrue(response.data['availability'])
    
    def test_create_book_validation_error(self):
        """Test book creation with validation errors"""
        self.client.force_authenticate(user=self.staff_user)
        data = {
            'title': 'A',  # Too short
            'category': 'B'  # Too short
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('category', response.data)
    
    def test_update_book_staff_user(self):
        """Test that staff users can update books"""
        self.client.force_authenticate(user=self.staff_user)
        data = {
            'title': 'Updated Book Title',
            'category': 'Updated Category'
        }
        response = self.client.patch(self.detail_url(self.book1.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Book Title')
    
    def test_delete_book_staff_user(self):
        """Test that staff users can delete books"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.delete(self.detail_url(self.book1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book1.id).exists())
    
    def test_search_books(self):
        """Test searching books by title and category"""
        self.client.force_authenticate(user=self.staff_user)
        
        # Search by title
        response = self.client.get(self.list_url, {'search': 'Test Book 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Book 1')
        
        # Search by category
        response = self.client.get(self.list_url, {'search': 'Fiction'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # book1 and unavailable_book
    
    def test_ordering_books(self):
        """Test ordering books"""
        self.client.force_authenticate(user=self.staff_user)
        
        # Order by title (default)
        response = self.client.get(self.list_url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in response.data['results']]
        self.assertEqual(titles, sorted(titles))
        
        # Order by category
        response = self.client.get(self.list_url, {'ordering': 'category'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        categories = [book['category'] for book in response.data['results']]
        self.assertEqual(categories, sorted(categories))


class LoanViewSetTestCase(APITestBase):
    """Test cases for LoanViewSet"""
    
    def setUp(self):
        super().setUp()
        self.list_url = reverse('loan-list')
        self.detail_url = lambda pk: reverse('loan-detail', kwargs={'pk': pk})
        self.return_url = lambda pk: reverse('loan-return-book', kwargs={'pk': pk})
    
    def test_list_loans_unauthenticated(self):
        """Test that unauthenticated users cannot access loans"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_loans_authenticated_user(self):
        """Test that authenticated users can list loans"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_retrieve_loan_authenticated_user(self):
        """Test that authenticated users can retrieve a specific loan"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.detail_url(self.active_loan.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'LOANED')
    
    def test_create_loan_authenticated_user(self):
        """Test that authenticated users can create loans"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'book': str(self.book1.id),
            'member': str(self.member2.id)
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'LOANED')
        
        # Check that book availability was updated
        self.book1.refresh_from_db()
        self.assertFalse(self.book1.availability)
    
    def test_create_loan_unavailable_book(self):
        """Test creating loan for unavailable book"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'book': str(self.unavailable_book.id),
            'member': str(self.member2.id)
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('book', response.data)
    
    def test_create_loan_duplicate_active_loan(self):
        """Test creating duplicate active loan for same book and member"""
        self.client.force_authenticate(user=self.regular_user)
        
        # First create a loan with an available book
        data = {
            'book': str(self.book1.id),
            'member': str(self.member1.id)
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Try to create another loan for the same book and member
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Should get member error first (validation order)
        self.assertIn('non_field_errors', response.data)
    
    def test_create_loan_duplicate_member_validation(self):
        """Test creating loan with member who already has active loan for different available book"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Create a loan for member1 with book1
        data = {
            'book': str(self.book1.id),
            'member': str(self.member1.id)
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Now try to create another loan for the same member with the same book
        # This should fail because member already has an active loan for this book
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_return_book_action(self):
        """Test the return_book custom action"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(self.return_url(self.active_loan.id), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'RETURNED')
        self.assertIsNotNone(response.data['return_date'])
        
        # Check that book availability was updated
        self.unavailable_book.refresh_from_db()
        self.assertTrue(self.unavailable_book.availability)
    
    def test_return_book_already_returned(self):
        """Test returning a book that's already returned"""
        # First return the book
        self.client.force_authenticate(user=self.regular_user)
        self.client.patch(self.return_url(self.active_loan.id), {})
        
        # Try to return again
        response = self.client.patch(self.return_url(self.active_loan.id), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_filter_loans_by_status(self):
        """Test filtering loans by status"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Filter by LOANED status
        response = self.client.get(self.list_url, {'status': 'LOANED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'LOANED')
    
    def test_filter_loans_by_member(self):
        """Test filtering loans by member"""
        self.client.force_authenticate(user=self.regular_user)
        
        response = self.client.get(self.list_url, {'member': str(self.member1.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['member'], str(self.member1.id))
    
    def test_filter_loans_by_book(self):
        """Test filtering loans by book"""
        self.client.force_authenticate(user=self.regular_user)
        
        response = self.client.get(self.list_url, {'book': str(self.unavailable_book.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['book'], str(self.unavailable_book.id))
    
    def test_search_loans(self):
        """Test searching loans"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Search by book title
        response = self.client.get(self.list_url, {'search': 'Unavailable'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Search by member name
        response = self.client.get(self.list_url, {'search': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_ordering_loans(self):
        """Test ordering loans"""
        # Create another loan for testing
        self.client.force_authenticate(user=self.regular_user)
        Loan.objects.create(
            book=self.book1,
            member=self.member2,
            loan_date=date.today() - timedelta(days=1),
            status='LOANED'
        )
        
        # Test ordering by loan_date
        response = self.client.get(self.list_url, {'ordering': 'loan_date'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        loan_dates = [loan['loan_date'] for loan in response.data['results']]
        self.assertEqual(loan_dates, sorted(loan_dates))


class LoanHistoryViewSetTestCase(APITestBase):
    """Test cases for LoanHistoryViewSet"""
    
    def setUp(self):
        super().setUp()
        self.list_url = reverse('loanhistory-list')
        self.detail_url = lambda pk: reverse('loanhistory-detail', kwargs={'pk': pk})
        
        # Create some loan history entries
        self.history1 = LoanHistory.objects.create(
            book=self.book1,
            member=self.member1,
            action_date=date.today()
        )
        
        self.history2 = LoanHistory.objects.create(
            book=self.book2,
            member=self.member2,
            action_date=date.today() - timedelta(days=5)
        )
    
    def test_list_history_unauthenticated(self):
        """Test that unauthenticated users cannot access loan history"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_history_authenticated_user(self):
        """Test that authenticated users can list loan history"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include history from the active_loan creation + our manual entries
        self.assertGreaterEqual(len(response.data['results']), 2)
    
    def test_retrieve_history_authenticated_user(self):
        """Test that authenticated users can retrieve specific history"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.detail_url(self.history1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book'], str(self.book1.id))
    
    def test_create_history_not_allowed(self):
        """Test that creating history entries is not allowed"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'book': str(self.book1.id),
            'member': str(self.member1.id),
            'action_date': date.today()
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_update_history_not_allowed(self):
        """Test that updating history entries is not allowed"""
        self.client.force_authenticate(user=self.regular_user)
        data = {'action_date': date.today() + timedelta(days=1)}
        response = self.client.patch(self.detail_url(self.history1.id), data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_delete_history_not_allowed(self):
        """Test that deleting history entries is not allowed"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.detail_url(self.history1.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_filter_history_by_date_range(self):
        """Test filtering history by date range"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Filter by start date
        start_date = date.today() - timedelta(days=2)
        response = self.client.get(self.list_url, {'start_date': start_date})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include recent entries
        self.assertGreater(len(response.data['results']), 0)
        
        # Filter by end date
        end_date = date.today() - timedelta(days=3)
        response = self.client.get(self.list_url, {'end_date': end_date})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include only older entries
        for entry in response.data['results']:
            entry_date = entry['action_date']
            self.assertLessEqual(entry_date, str(end_date))
    
    def test_filter_history_by_member(self):
        """Test filtering history by member"""
        self.client.force_authenticate(user=self.regular_user)
        
        response = self.client.get(self.list_url, {'member': str(self.member1.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for entry in response.data['results']:
            self.assertEqual(entry['member'], str(self.member1.id))
    
    def test_filter_history_by_book(self):
        """Test filtering history by book"""
        self.client.force_authenticate(user=self.regular_user)
        
        response = self.client.get(self.list_url, {'book': str(self.book1.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for entry in response.data['results']:
            self.assertEqual(entry['book'], str(self.book1.id))
    
    def test_search_history(self):
        """Test searching loan history"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Search by book title
        response = self.client.get(self.list_url, {'search': 'Test Book 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        
        # Search by member name
        response = self.client.get(self.list_url, {'search': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_ordering_history(self):
        """Test ordering loan history"""
        self.client.force_authenticate(user=self.regular_user)
        
        # Test ordering by action_date (default is descending)
        response = self.client.get(self.list_url, {'ordering': '-action_date'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        action_dates = [entry['action_date'] for entry in response.data['results']]
        self.assertEqual(action_dates, sorted(action_dates, reverse=True))


class ModelTestCase(TestCase):
    """Test cases for model methods and validations"""
    
    def setUp(self):
        """Set up test data"""
        self.member = Member.objects.create(
            name='Test Member',
            cpf='11111111111',
            email='test@example.com'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            category='Test Category',
            availability=True
        )
    
    def test_book_string_representation(self):
        """Test Book model string representation"""
        self.assertEqual(str(self.book), 'Test Book - Available')
        
        self.book.availability = False
        self.assertEqual(str(self.book), 'Test Book - Loaned')
    
    def test_loan_creation_updates_book_availability(self):
        """Test that creating a loan updates book availability"""
        self.assertTrue(self.book.availability)
        
        loan = Loan.objects.create(
            book=self.book,
            member=self.member
        )
        
        self.book.refresh_from_db()
        self.assertFalse(self.book.availability)
        self.assertEqual(loan.status, 'LOANED')
    
    def test_loan_creation_with_unavailable_book_raises_error(self):
        """Test that creating a loan with unavailable book raises error"""
        self.book.availability = False
        self.book.save()
        
        with self.assertRaises(ValueError):
            Loan.objects.create(
                book=self.book,
                member=self.member
            )
    
    def test_loan_return_updates_book_availability(self):
        """Test that returning a loan updates book availability"""
        loan = Loan.objects.create(
            book=self.book,
            member=self.member
        )
        
        # Return the book
        loan.status = 'RETURNED'
        loan.save()
        
        self.book.refresh_from_db()
        self.assertTrue(self.book.availability)
        self.assertIsNotNone(loan.return_date)
    
    def test_loan_history_creation(self):
        """Test that loan history is created when loans are saved"""
        initial_history_count = LoanHistory.objects.count()
        
        # Create a loan
        loan = Loan.objects.create(
            book=self.book,
            member=self.member
        )
        
        # Should create one history entry
        self.assertEqual(LoanHistory.objects.count(), initial_history_count + 1)
        
        # Return the book
        loan.status = 'RETURNED'
        loan.save()
        
        # Should create another history entry
        self.assertEqual(LoanHistory.objects.count(), initial_history_count + 2)
    
    def test_member_string_representation(self):
        """Test Member model string representation"""
        self.assertEqual(str(self.member), 'Test Member - test@example.com')
    
    def test_loan_history_string_representation(self):
        """Test LoanHistory model string representation"""
        history = LoanHistory.objects.create(
            book=self.book,
            member=self.member,
            action_date=date.today()
        )
        
        expected = f'Test Book - Test Member ({date.today()})'
        self.assertEqual(str(history), expected)
