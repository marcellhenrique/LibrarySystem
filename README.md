# 📚 Library Management System

A modern library management system built with Django and React-like frontend. This application provides a user-friendly interface for managing books, members, and loans with real-time updates and comprehensive history tracking.

![Django](https://img.shields.io/badge/Django-5.2.1-092E20?style=flat&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.16.0-ff1709?style=flat&logo=django&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.x-38B2AC?style=flat&logo=tailwind-css&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)

## 🎯 Features

### Frontend Features
- **Modern UI**: Clean and responsive interface built with TailwindCSS
- **Real-time Updates**: Dynamic content loading without page refreshes
- **Search & Filters**: Instant search across books, members, and loans
- **Loan Management**: Easy-to-use interface for loan creation and returns
- **History Tracking**: Visual history of all library transactions
- **Form Validation**: Client-side validation with clear error messages
- **Mobile Responsive**: Optimized for all device sizes

### Backend Features
- **RESTful API**: Complete API for all library operations
- **Authentication**: JWT-based authentication system
- **Data Validation**: Comprehensive server-side validation
- **History Logging**: Automatic tracking of all transactions
- **Search Capability**: Advanced search across all entities

## 🖥️ User Interface

### Main Sections
- **Dashboard**: Overview of library activity
- **Books Management**: List, add, and manage books
- **Member Management**: Member registration and management
- **Active Loans**: Current loan tracking
- **Loan History**: Complete transaction history

### Key UI Components
- **Search Bar**: Global search functionality
- **Status Filters**: Filter loans by status
- **Modal Forms**: Clean forms for adding books/members
- **Status Indicators**: Visual indicators for loan status
- **Responsive Tables**: Mobile-friendly data display

## 🗄️ Data Models

### Books
- `id`: UUID
- `title`: String (Required)
- `category`: String (Required)
- `availability`: Boolean
- `created_at`, `updated_at`: Timestamps

### Members
- `id`: UUID
- `name`: String (Min length: 3)
- `cpf`: String (11 digits)
- `phone`: String (10-15 digits, Optional)
- `email`: Email (Unique)

### Loans
- `id`: UUID
- `book`: Book Reference
- `member`: Member Reference
- `loan_date`: Timestamp
- `return_date`: Timestamp
- `status`: LOANED | RETURNED

### Loan History
- `id`: UUID
- `book`: Book Reference
- `member`: Member Reference
- `action_type`: LOANED | RETURNED
- `action_date`: Timestamp

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+ (for development)
- Git

### Local Development Setup

1. **Clone and setup virtual environment**
   ```bash
   git clone <repository-url>
   cd LibrarySystem
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run the development server**
   ```bash
   python manage.py runserver
   ```

5. **Access the application**
   - Main Interface: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin/
   - API Documentation: http://localhost:8000/swagger/
   ```

4. **Run migrations and start server**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py runserver
   ```

The application will use the `.env.local` file for local development, which configures the database connection to `localhost:5432`.

## 🔗 API Endpoints

### Authentication
- `POST /api/accounts/users/login/` - Staff login
- `POST /api/accounts/token/refresh/` - Refresh JWT token

### Books
- `GET /api/books/` - List all books
- `POST /api/books/` - Create new book
- `GET /api/books/{id}/` - Get book details
- `PUT /api/books/{id}/` - Update book
- `DELETE /api/books/{id}/` - Delete book

### Members
- `GET /api/accounts/members/` - List all members
- `POST /api/accounts/members/` - Register new member
- `GET /api/accounts/members/{id}/` - Get member details
- `PUT /api/accounts/members/{id}/` - Update member
- `DELETE /api/accounts/members/{id}/` - Delete member

### Loans
- `GET /api/loans/` - List all loans (with filters)
- `POST /api/loans/` - Create new loan
- `GET /api/loans/{id}/` - Get loan details
- `PATCH /api/loans/{id}/return_book/` - Process book return

### Loan History
- `GET /api/history/` - View loan history (with filters)

### Staff Management
- `GET /api/accounts/users/` - List staff members
- `POST /api/accounts/users/` - Create staff member
- `GET /api/accounts/users/profile/` - Get current user profile

## 📋 API Usage Examples

### Authentication
```bash
# Login
curl -X POST http://localhost:8000/api/accounts/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"login": "admin", "password": "password"}'
```

### Create a Book
```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"title": "Django for Beginners", "category": "Programming"}'
```

### Register a Member
```bash
curl -X POST http://localhost:8000/api/accounts/members/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"name": "John Doe", "cpf": "12345678901", "email": "john@example.com", "phone": "1234567890"}'
```

### Create a Loan
```bash
curl -X POST http://localhost:8000/api/loans/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"book": "<book_id>", "member": "<member_id>"}'
```

### Return a Book
```bash
curl -X PATCH http://localhost:8000/api/loans/<loan_id>/return_book/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{}'
```

## 🔍 Query Parameters & Filters

### Books
- `search`: Search by title or category
- `ordering`: Sort by title, category, or created_at

### Members
- `search`: Search by name, email, or CPF

### Loans
- `status`: Filter by LOANED or RETURNED
- `member`: Filter by member ID
- `book`: Filter by book ID
- `search`: Search by book title, member name, or status

### Loan History
- `start_date` & `end_date`: Filter by date range
- `member`: Filter by member ID
- `book`: Filter by book ID
- `search`: Search by book title or member name

## 🎨 Styling

The application uses a combination of TailwindCSS and custom styles:

### Core Components
- `.form-input`: Styled form inputs with visible outlines
- `.form-label`: Form labels with proper spacing
- `.btn-primary`: Primary action buttons
- `.btn-secondary`: Secondary action buttons
- `.card`: Content card containers

### Animation
- `.fade-in`: Smooth fade-in animation for dynamic content

## 🔍 Search & Filters

### Global Search
- Search across books and members
- Instant results as you type
- Highlights matching content

### Loan Filters
- Filter by status (LOANED/RETURNED)
- Filter by date range
- Combine with search terms

## 📱 Responsive Design

- Mobile-first approach
- Responsive navigation
- Adaptive layouts
- Touch-friendly interfaces

## 🔧 Configuration

### Environment Variables
- `DEBUG`: Enable/disable debug mode
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: Database connection string
- `ALLOWED_HOSTS`: Allowed host names

### Development Tools
- Django Debug Toolbar (in development)
- Django Extensions
- DRF Browsable API

## 🔐 Security Features

### Authentication
- JWT-based token authentication
- Secure password hashing
- Role-based access control

### Data Protection
- Input validation and sanitization
- CSRF protection
- XSS prevention

### API Security
- Token refresh mechanisms
- Request rate limiting
- Secure password handling

## 🚦 Getting Started Checklist

- [ ] Clone the repository
- [ ] Start with `docker-compose up --build`
- [ ] Access API documentation at http://localhost:8000/swagger/
- [ ] Create a superuser: `docker-compose exec web python manage.py createsuperuser`
- [ ] Access admin panel at http://localhost:8000/admin/
- [ ] Test API endpoints using the provided examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 📞 Support

For questions or support, please open an issue in the repository or contact the development team.

---

**Built with ❤️ using Django Rest Framework**
