# Library Service
This project is a library service with both an Admin API and a Public API, using Flask, SQLAlchemy (SQLite as the database), and Docker for containerization.

### Project Overview
- **Admin API**: Provides administrative features such as managing books and users.
- **Public API**: Allows users to browse books, borrow them, and track their borrowing status.
- **SQLite**: Used as the database for storing user and book information.

### Prerequisites
Make sure you have Docker installed on your machine:

### Project Structure
```
├── admin
│   ├── api.py         # Admin API (Flask application) 
├── public
│   ├── api.py         # Public API (Flask application)
├── Dockerfile.admin    # Dockerfile for the Admin service
├── Dockerfile.public   # Dockerfile for the Public service
├── docker-compose.yml  # Docker Compose configuration
└── README.md           # You're reading this now
```

### Running the Project
1. Clone the repository:
```bash
git clone <repository-url>
cd library-service
```
2. Build and start the containers:
```bash
docker-compose up --build
```

3. Access the services:
- **Admin API**: Available at http://localhost:2324
- **Public API**: Available at http://localhost:2323


### API Endpoints
- **Admin API**:
    - `GET /api/users/`: Get all users
    - `GET /api/user/<user_id>`: Get a user by ID
    - `/api/users/books/`: Get list of users & their borrowed books
    - `POST /api/books/`: Add a new book
    - `GET /api/books/`: Get all books
    - `GET /api/books/<book_id>`: Get a book by ID
    - `PUT /api/books/<book_id>`: Update a book
    - `GET /api/borrowed/`: Get all borrowed books

- **Public API**:
    - `GET /api/public/books/`: Get all available books
    - `GET /api/public/books/<book_id>`: Get a book by ID
    - `POST /api/public/user/`:  Register a new user
    - `GET /api/public/filter/books`: Filter books by publisher & category`
    - `PUT /api/public/borrow/`: Borrow a book