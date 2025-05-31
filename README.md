# 📚 Django Library Management System

A comprehensive REST API built with Django Rest Framework for managing a library system. This application allows management of books, members, staff, and loan processes with full history tracking.

![Django](https://img.shields.io/badge/Django-5.2.1-092E20?style=flat&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.16.0-ff1709?style=flat&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=flat&logo=docker&logoColor=white)

## 🎯 Features

- **Book Management**: Create, read, update, and delete books with category and availability tracking
- **Member Management**: Comprehensive member registration with CPF, email, and phone validation
- **Staff Authentication**: JWT-based authentication system for library staff
- **Loan System**: Complete loan workflow with automatic availability tracking
- **Return Processing**: Streamlined book return process with history logging
- **Loan History**: Complete audit trail of all library transactions
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Containerized**: Full Docker support with PostgreSQL database

## 🗄️ Data Models

### Books
- `id`: UUID (Primary Key)
- `title`: String (Required)
- `category`: String (Required)
- `availability`: Boolean (Auto-managed)
- `created_at`, `updated_at`: Timestamps

### Members
- `id`: UUID (Primary Key)
- `name`: String (Required)
- `cpf`: 11-digit string (Unique, Required)
- `phone`: 10-15 digit string (Optional)
- `email`: Email (Unique, Required)
- `created_at`, `updated_at`: Timestamps

### Staff Users
- `id`: UUID (Primary Key)
- `login`: String (Unique, Required)
- `email`: Email (Unique, Required)
- `name`: String (Required)
- `role`: String (Required)
- `password`: Hashed password

### Loans
- `id`: UUID (Primary Key)
- `book`: Foreign Key to Book
- `member`: Foreign Key to Member
- `loan_date`: Date (Auto-set)
- `return_date`: Date (Set on return)
- `status`: LOANED | RETURNED

### Loan History
- `id`: UUID (Primary Key)
- `book`: Foreign Key to Book
- `member`: Foreign Key to Member
- `action_date`: Date of transaction
- `created_at`: Timestamp

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LibrarySystem
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - API: http://localhost:8000/api/
   - Admin Panel: http://localhost:8000/admin/
   - API Documentation: http://localhost:8000/swagger/

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

3. **Start PostgreSQL database container**
   ```bash
   docker-compose up db -d
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

## 🏗️ Project Structure

```
LibrarySystem/
├── 📁 accounts/           # User and member management
├── 📁 api/               # Core library API (books, loans, history)
├── 📁 config/            # Django project settings
├── 📁 staticfiles/       # Static files
├── 📄 docker-compose.yml # Docker orchestration
├── 📄 Dockerfile         # Application container
├── 📄 requirements.txt   # Python dependencies
├── 📄 .env.local         # Local development environment
├── 📄 entrypoint.sh      # Container startup script
└── 📄 manage.py          # Django management script
```

## ⚙️ Business Rules

- **Book Loans**: Only available books can be loaned
- **Availability Management**: Book availability is automatically updated on loan/return
- **Loan Status**: Automatically managed (LOANED → RETURNED)
- **History Tracking**: All loan/return actions are logged
- **Authentication**: All API endpoints require staff authentication
- **Validation**: Comprehensive validation for CPF, email, and phone formats

## 🔧 Environment Configuration

### Docker Environment Variables
Set in `docker-compose.yml`:
- `POSTGRES_DB=library_system`
- `POSTGRES_USER=library_user`
- `POSTGRES_PASSWORD=library_password`
- `POSTGRES_HOST=db`
- `DEBUG=1`

### Local Development Environment
Set in `.env.local`:
- `POSTGRES_HOST=localhost` (connects to containerized DB)
- All other database settings remain the same

## 📊 Features & Capabilities

### 🔐 Security
- JWT-based authentication with refresh tokens
- Password hashing with Django's built-in security
- CORS configuration for cross-origin requests
- Input validation and sanitization

### 📈 Monitoring & Logging
- Comprehensive logging to file and console
- Request/response tracking
- Error handling and reporting

### 🔍 API Documentation
- Auto-generated Swagger UI at `/swagger/`
- ReDoc documentation at `/redoc/`
- OpenAPI 3.0 specification

### 🐳 Docker Features
- Multi-container setup with PostgreSQL 14
- Health checks for database connectivity
- Volume persistence for data
- Automated migrations and static file collection
- Production-ready Gunicorn WSGI server

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
