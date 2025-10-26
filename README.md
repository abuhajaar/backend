# OpenBO Backend

A Flask-based REST API backend with MariaDB database integration using Clean Architecture.

## Features

- Flask web framework
- MariaDB database integration
- SQLAlchemy ORM
- CORS enabled
- Environment-based configuration
- Clean Architecture (Handler, UseCase, Repository)
- **JWT Authentication**
- **Password Hashing (bcrypt)**
- **User Management with Roles**

## Prerequisites

- Python 3.8 or higher
- MariaDB/MySQL server installed and running

## Installation

1. **Create a virtual environment:**
   ```powershell
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Update the database credentials in `.env` file

5. **Create the database:**
   ```sql
   CREATE DATABASE openbo_db;
   ```

6. **Run migrations:**
   ```powershell
   python migrate.py
   ```

7. **Seed initial data:**
   ```powershell
   python seed.py
   ```

## Running the Application

1. Make sure MariaDB is running
2. Activate the virtual environment (if not already activated)
3. Run the Flask application:
   ```powershell
   python run.py
   ```

The server will start at `http://localhost:5000`

## API Endpoints

### Authentication
- **POST** `/api/auth/login`
  - Login with username and password
  - Body: `{ username: string, password: string }`
  - Response: `{ success: true, data: { user: {...}, access_token: string, token_type: "Bearer" } }`

- **POST** `/api/auth/register`
  - Register new user
  - Body: `{ username, email, password, phone?, role?, department_id? }`
  - Response: `{ success: true, data: {...} }`

- **GET** `/api/auth/me` (Protected)
  - Get current user info
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ success: true, data: {...} }`

### Health Check
- **GET** `/api/health`
  - Returns server status

### Users
- **GET** `/api/users`
  - Get all users
  - Response: `{ success: true, data: [...], count: number }`

- **GET** `/api/users/:id`
  - Get user by ID
  - Response: `{ success: true, data: {...} }`

- **POST** `/api/users`
  - Create a new user
  - Body: `{ name: string, email: string }`
  - Response: `{ success: true, data: {...} }`

- **PUT** `/api/users/:id`
  - Update user
  - Body: `{ name: string, email: string }`
  - Response: `{ success: true, data: {...} }`

- **DELETE** `/api/users/:id`
  - Delete user
  - Response: `{ success: true, message: string }`

## Database Schema

### Users Table
- `id` - Integer (Primary Key, Auto Increment)
- `name` - String(100)
- `email` - String(120, Unique)
- `created_at` - DateTime
- `updated_at` - DateTime

## Project Structure (Clean Architecture)

```
backend/
├── src/
│   ├── __init__.py
│   ├── app.py                      # Application factory
│   ├── config/
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration settings
│   │   └── database.py             # Database initialization
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py                 # User model
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── user_repository.py      # User data access layer
│   ├── usecases/
│   │   ├── __init__.py
│   │   └── user_usecase.py         # User business logic
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── user_controller.py      # User request handlers
│   │   └── health_controller.py    # Health check handler
│   └── routes/
│       ├── __init__.py
│       ├── user_routes.py          # User endpoint definitions
│       └── health_routes.py        # Health check endpoint
├── run.py                          # Entry point
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables
├── .env.example                   # Example environment file
└── README.md                      # This file
```

## Architecture Layers

### 1. **Routes** (Routing Layer)
- Definisi endpoint dan HTTP methods
- Mapping URL ke controller functions
- Menggunakan Flask Blueprint

### 2. **Controllers** (Presentation Layer)
- Menangani HTTP requests dan responses
- Validasi input dasar
- Memanggil UseCase untuk business logic
- Format response

### 3. **UseCases** (Business Logic Layer)
- Berisi business logic dan rules
- Orchestrate flow data antara controllers dan repositories
- Validasi business rules

### 4. **Repositories** (Data Access Layer)
- Menangani semua operasi database
- Abstraksi untuk data persistence
- CRUD operations

### 5. **Models** (Entity Layer)
- Definisi struktur data
- Database schema
- Data transformation methods

## Development

The application runs in debug mode by default. For production, make sure to:
- Set `SECRET_KEY` to a secure random value
- Set `SQLALCHEMY_ECHO` to `False` in `config.py`
- Use a production WSGI server (gunicorn, uWSGI, etc.)
