## openBO — Backend (Penjelasan dalam Bahasa Indonesia)

Backend untuk sistem booking openBO menggunakan Flask dan MariaDB. Struktur mengikuti prinsip Clean Architecture: Routes → Controllers → UseCases → Repositories → Models.

Ringkasan singkat:
- Bahasa: Python (Flask)
- Database: MariaDB (mysql+pymysql)
- ORM: SQLAlchemy
- Autentikasi: JWT (PyJWT) + bcrypt untuk hashing password

README ini menjelaskan struktur folder, alur request → response, serta poin penting seperti logika ketersediaan ruang, migrasi, dan seeding.

## Struktur folder (inti)

File utama di root:
- `run.py` — entrypoint aplikasi lokal
- `migrate.py` — script migrasi sederhana (menciptakan/mereset tabel)
- `seed.py` — script untuk mengisi data awal (users, floors, spaces, amenities, bookings, blackouts)

Direktori `src/` (kode sumber):
- `src/app.py` — application factory, inisialisasi Flask dan blueprint
- `src/config/` — konfigurasi & `database.py` (instance SQLAlchemy)
- `src/routes/` — definisi endpoint Flask (meneruskan ke controller)
- `src/controllers/` — menangani request, memanggil usecase, memformat response
- `src/usecases/` — logika bisnis (mis. pemeriksaan availability, aturan booking)
- `src/repositories/` — akses database via SQLAlchemy (dipisah untuk testabilitas)
- `src/models/` — model SQLAlchemy (User, Department, Floor, Space, Amenity, Blackout, Booking)
- `src/utils/` — helper (JWT helper, response template, error handlers)

Contoh file penting:
- `src/routes/space_routes.py`
- `src/controllers/space_controller.py`
- `src/usecases/space_usecase.py` (logika ketersediaan)
- `src/repositories/space_repository.py`

## Alur data (request → response)

1. Client mengirim HTTP request (mis. `GET /api/spaces`).
2. Route di `src/routes` menerima request dan mem-forward ke controller.
3. Controller mem-parse dan memvalidasi parameter/body lalu memanggil UseCase.
4. UseCase menjalankan aturan bisnis dan memanggil repository untuk mengambil/menyimpan data.
5. Repository melakukan query ke database melalui model SQLAlchemy.
6. Model mengembalikan objek ke UseCase.
7. UseCase membentuk hasil domain (mis. menghitung `available_hours`) dan mengembalikan ke controller.
8. Controller membungkus hasil menggunakan `ResponseTemplate` dan mengembalikan HTTP response ke client.

Pisahan tanggung jawab ini membuat controller tipis, usecase berfokus pada logika bisnis, dan repository mengurus akses data.

## Logika ketersediaan ruang (ringkas)

Query yang biasanya dipakai client:
- `date` — format YYYY-MM-DD
- `start_time`, `end_time` — format HH:MM (24 jam)

Langkah ketika date dan time diberikan:
1. UseCase mem-parse dan memvalidasi format `date`, `start_time`, `end_time`.
2. Ambil seluruh booking relevan untuk setiap space pada tanggal tersebut (kecualikan booking yang cancelled bila perlu).
3. Periksa `opening_hours` masing-masing space (disimpan sebagai JSON per-hari) — jika tutup maka tidak tersedia.
4. Terapkan `buffer_min` di sekitar setiap booking (baik dari snapshot booking atau default space) sehingga interval terpakai melebar ke depan/ke belakang.
5. Gabungkan interval yang saling tumpang tindih lalu hitung celah (gaps) antara jam buka dan jam tutup setelah mengeluarkan interval terpakai.
6. Hasil celah tersebut adalah `available_hours` (array object {start: "HH:MM", end: "HH:MM"]).
7. Jika `available_hours` kosong untuk tanggal yang diminta, space dianggap TIDAK tersedia; saat client memakai filter tanggal/waktu, space yang tidak tersedia tidak akan dikirimkan.

Perilaku penting:
- Jika client tidak mengirim `date`, server mengembalikan semua spaces tanpa keterangan `available_hours`.
- Jika `date` dikirim, response menyertakan `available_hours` dan `is_available` bila relevan.
- Space tanpa jam tersedia (array kosong) akan di-skip pada hasil ketika filter tanggal/waktu dipakai.

## Contoh endpoint & format

- POST `/api/login` — body: {"username":"...","password":"..."} → mengembalikan JWT
- POST `/api/register` — membuat user (password di-hash dengan bcrypt)
- GET `/api/spaces` — optional query params: `date`, `start_time`, `end_time`

Contoh:
`GET /api/spaces?date=2025-01-05&start_time=09:00&end_time=10:00`

Contoh response (disingkat):

```
{
  "status": "success",
  "data": [
    {
      "id": 4,
      "name": "Ruang Semeru",
      "location": "Lantai 12",
      "is_available": true,
      "available_hours": [ {"start":"08:00","end":"12:00"}, {"start":"14:00","end":"18:00"} ],
      ...
    }
  ]
}
```

Hanya spaces yang memiliki slot tersedia untuk filter yang dikirim akan dikembalikan.

## Cara menjalankan lokal (PowerShell)

1. Buat virtual environment dan install dependency:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Konfigurasi koneksi database di `src/config/config.py` (contoh: `mysql+pymysql://user:pass@host/dbname`).

3. Jalankan migrasi (script sederhana yang recreate tabel):

```powershell
python migrate.py
```

4. Seed data awal:

```powershell
python seed.py
```

5. Jalankan server:

```powershell
python run.py
```

Default server: `0.0.0.0:5000` (bisa diubah di `run.py`).

## Catatan: foreign key sirkular (users ↔ departments)

Ada relasi sirkular:
- `users.department_id` → `departments.id`
- `departments.manager_id` → `users.id`

Beberapa GUI database dapat menampilkan tabel `users` sebagai read-only karena relasi sirkular ini. Namun perubahan tetap bisa dilakukan melalui API atau SQL.

Cara aman mengubah data user:
- Lewat API aplikasi (direkomendasikan).
- Atau langsung SQL (hati‑hati):

```sql
SET FOREIGN_KEY_CHECKS = 0;
UPDATE users SET email = 'baru@company.com' WHERE id = 1;
SET FOREIGN_KEY_CHECKS = 1;
```

Jika ingin menghindari masalah GUI, opsi jangka panjang: hapus FK sirkular dan tangani konsistensi lewat aplikasi, atau gunakan desain referensi terpisah.

## Rekomendasi & langkah berikutnya

- Tambah dokumentasi OpenAPI / Swagger untuk contract API.
- Tambah unit test untuk logika `available_hours` (happy path + edge cases seperti overlap buffer, blackout).
- Tambah endpoint CRUD untuk Spaces/Bookings agar pengelolaan data tidak perlu akses DB langsung.

---

Jika Anda mau, saya bisa lanjut membuat OpenAPI spec otomatis atau menambahkan endpoint CRUD untuk manajemen user/space.
## openBO - Backend

Backend for the openBO booking system (Flask + MariaDB) — small, clean-architecture project with routes, controllers, use cases, repositories and models.

## Quick overview

- Language: Python (Flask)
- Database: MariaDB (mysql+pymysql)
- ORM: SQLAlchemy
- Auth: JWT (PyJWT) + bcrypt password hashing
- Architecture: Clean Architecture (Routes → Controllers → UseCases → Repositories → Models)

This README documents the folder structure, the request → response data flow, and how key features (availability logic, seeding, migrations) work.

## Folder structure

Root files:
- `run.py` — application entrypoint for local development
- `migrate.py` — simple migration script (creates/drops tables)
- `seed.py` — seeds initial data (users, floors, spaces, amenities, bookings, blackouts)

Key source tree (`src/`):

- `src/app.py` — application factory, Flask app creation and blueprint registration
- `src/config/` — configuration and `database.py` (SQLAlchemy db instance)
- `src/routes/` — Flask route definitions (thin wrappers that call controllers)
- `src/controllers/` — controllers that parse request data, call usecases, and prepare responses
- `src/usecases/` — business logic (availability checks, booking rules, validation)
- `src/repositories/` — DB access (queries), isolated for testability
- `src/models/` — SQLAlchemy models (User, Department, Floor, Space, Amenity, Blackout, Booking)
- `src/utils/` — helpers (JWT encoding/decoding, response templates, error handlers)

Example files you will see:
- `src/routes/space_routes.py`
- `src/controllers/space_controller.py`
- `src/usecases/space_usecase.py` (availability logic)
- `src/repositories/space_repository.py`

## Data flow (high level)

1. Client makes HTTP request to an endpoint (e.g., `GET /api/spaces`)
2. Route handler in `src/routes` receives the request and forwards it to a controller
3. Controller (in `src/controllers`) extracts and validates query params/payload, then calls a UseCase
4. UseCase (in `src/usecases`) contains business rules and orchestrates repository calls to fetch/persist data
5. Repositories (in `src/repositories`) perform SQLAlchemy queries against models
6. Models (in `src/models`) map to DB tables; repositories return model instances to usecases
7. UseCase formats the domain result and returns to Controller
8. Controller wraps the result with `ResponseTemplate` and returns HTTP response

This separation keeps controllers thin, usecases focused on rules, and repositories responsible for DB access.

## Availability & booking logic (how it is processed)

- Request parameters for availability (spaces endpoint):
  - `date` — YYYY-MM-DD
  - `start_time`, `end_time` — HH:MM (24h)

- When client provides date and times, the UseCase will:
  1. Parse and validate `date`, `start_time`, `end_time`.
  2. For each space, load bookings for that date (excluding cancelled as appropriate).
  3. Consider `opening_hours` (stored per-space as JSON) to determine whether the date is open.
  4. Apply `buffer_min` (snapshot at booking time or space default) around bookings to compute true occupied intervals.
  5. Compute `available_hours` as gaps between opening and closing times after excluding occupied intervals.
  6. If `available_hours` is empty for that date, the space is considered NOT available; when filters were provided, such spaces are skipped from the response.

- Important behaviors implemented:
  - If no `date` provided, response returns all spaces (no availability filtering).
  - If `date` provided, response includes `available_hours` (array of {start: "HH:MM", end: "HH:MM"}) and `is_available` when relevant.
  - If `available_hours` is empty for a space on the requested date, the space will not be included in the filtered response (client requested a time window but the space has no free periods).

## Common endpoints (examples)

- POST /api/login — body:{"username":"...","password":"..."} → returns JWT
- POST /api/register — simple user creation (password hashed with bcrypt)
- GET /api/spaces — query params optional `date`, `start_time`, `end_time`

GET /api/spaces example (filter availability):

`GET /api/spaces?date=2025-01-05&start_time=09:00&end_time=10:00`

Response:

```
{
  "status": "success",
  "data": [
    {
      "id": 4,
      "name": "Ruang Semeru",
      "location": "Lantai 12",
      "is_available": true,
      "available_hours": [ {"start":"08:00","end":"12:00"}, {"start":"14:00","end":"18:00"} ],
      ...
    }
    // other spaces that are available for the requested date/time
  ]
}
```

Note: spaces that do not have any available_hours for that date are not returned when client supplies date/time filters.

## How to run locally

1. Create a virtualenv and install requirements

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configure `src/config/config.py` with your MariaDB connection string (e.g., `mysql+pymysql://user:pass@host/dbname`).

3. Run migrations (this project uses a small `migrate.py` script that recreates tables):

```powershell
python migrate.py
```

4. Seed initial data (creates users, floors, spaces, amenities, bookings):

```powershell
python seed.py
```

5. Start the app:

```powershell
python run.py
```

Server will listen on 0.0.0.0:5000 by default (configurable in `run.py`).

## Editing users & circular FK note

There is a circular foreign-key relationship between `users.department_id` and `departments.manager_id`. Some DB GUIs may show `users` as read-only because of that circular reference. Edit users safely via:

- The application/API (preferred): use endpoints to update users
- Direct SQL: temporarily disable foreign key checks:

```sql
SET FOREIGN_KEY_CHECKS = 0;
UPDATE users SET email = 'new@company.com' WHERE id = 1;
SET FOREIGN_KEY_CHECKS = 1;
```

## Notes & future work

- Consider adding CRUD endpoints for spaces/bookings for easier management.
- Add unit tests around the availability calculation (happy path + edge cases: bookings touching buffer windows, blackout days).
- If you plan to use GUI DB tools often, consider removing the circular FK (store manager_id nullable and assign via app-level checks) or use deferred constraints if supported.

---

If you'd like, I can also add API docs or OpenAPI spec next. 
# OpenBO Backend

A Flask-based REST API backend with MariaDB database integration using Clean Architecture.

## Features

- Flask web framework
- MariaDB database integration
- SQLAlchemy ORM
- CORS enabled
- Environment-based configuration
- Clean Architecture (Routes → Controllers → UseCases → Repositories → Models)
- **JWT Authentication with Bearer token**
- **Password Hashing (bcrypt)**
- **User Management with Roles (employee, admin, manager)**
- **Space Management with availability checking**
- **Booking System with checkin/checkout**
- **Statistics for employees (today bookings, upcoming bookings, weekly hours, favorite space)**
- **Standardized API responses**
- **Global error handling**

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

### Option 1: Local Development

1. Make sure MariaDB is running
2. Activate the virtual environment (if not already activated)
3. Run the Flask application:
   ```powershell
   python run.py
   ```

The server will start at `http://localhost:5000`

### Option 2: Docker (Recommended)

See [DOCKER.md](DOCKER.md) for detailed Docker setup guide.

**Quick Start:**

```powershell
# Build and start all services (Flask + MariaDB)
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

**Access:**
- API: http://localhost:5000
- Database: localhost:3306

**Stop:**
```powershell
docker-compose down
```

For more Docker commands and troubleshooting, see [DOCKER.md](DOCKER.md).

### Option 3: Coolify Deployment (Production)

See [COOLIFY.md](COOLIFY.md) for detailed Coolify deployment guide.

**Pre-deployment checklist:** [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

**Quick Deploy:**
1. Connect Git repository to Coolify
2. Set environment variables in Coolify UI
3. Deploy
4. Run migrations via Coolify shell
5. Done!

For complete guide, see [COOLIFY.md](COOLIFY.md).

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

### Spaces
#### User Endpoints (Protected - Employee, Admin, Manager)
- **GET** `/api/spaces` (Protected)
  - Get all spaces with optional availability filter
  - Headers: `Authorization: Bearer <token>`
  - Query params: `date` (YYYY-MM-DD), `start_time` (HH:MM), `end_time` (HH:MM)
  - Response: `{ success: true, data: [...], message: "...", status_code: 200 }`
  - Space includes: `id`, `name`, `type`, `capacity`, `location`, `opening_hours`, `max_duration`, `status`, `amenities`, `is_available`, `available_hours`
  - Availability logic:
    - Without `date`: Returns all spaces without availability info
    - With `date` only: Returns spaces with `available_hours` for that day
    - With `date`, `start_time`, `end_time`: Returns only available spaces for that time slot
    - Checks: Opening hours, blackout dates, existing bookings, time conflicts

- **GET** `/api/spaces/:id` (Protected)
  - Get space by ID with detailed information
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ success: true, data: {...} }`

#### Management Endpoints (Protected - Superadmin Only)
- **GET** `/api/spaces/manage` (Superadmin)
  - Get all spaces for management
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ success: true, data: [...], message: "...", status_code: 200 }`
  - Returns all spaces with floor and amenity details

- **GET** `/api/spaces/manage/:id` (Superadmin)
  - Get space by ID for management
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ success: true, data: {...} }`

- **PUT** `/api/spaces/manage/:id` (Superadmin)
  - Update space status only
  - Headers: `Authorization: Bearer <token>`
  - Body: `{ status: "available" | "booked" | "in_maintenance" }`
  - Response: `{ success: true, data: {...}, message: "Status space berhasil diupdate", status_code: 200 }`
  - Note: Superadmin can only change space status. Space creation/deletion is managed via seed data.

### Bookings
#### User Endpoints (Protected - Employee, Admin, Manager)
- **POST** `/api/bookings` (Protected)
  - Create new booking
  - Headers: `Authorization: Bearer <token>`
  - Body: `{ user_id: number, space_id: number, start_at: "YYYY-MM-DD HH:MM:SS", end_at: "YYYY-MM-DD HH:MM:SS" }`
  - Response: `{ success: true, data: {...}, message: "Booking berhasil dibuat", status_code: 201 }`
  - Returns: booking with `checkin_code` (CHK-XXXXXXXX)
  - Validation:
    - Start time must be before end time
    - Cannot book in the past
    - Space must be available
    - Checks blackout dates
    - Checks opening hours
    - Validates max duration
    - Checks time conflicts with existing bookings

- **GET** `/api/bookings/:id` (Protected)
  - Get booking by ID
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ success: true, data: {...} }`

- **GET** `/api/bookings` (Protected)
  - Get all bookings
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ success: true, data: [...] }`

- **GET** `/api/bookings/user/:user_id` (Protected)
  - Get all bookings by user
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ success: true, data: [...] }`

- **PATCH** `/api/bookings/:id` (Protected)
  - Update booking status (checkin, checkout, cancel)
  - Headers: `Authorization: Bearer <token>`
  - Body for **checkin**: `{ status: "checkin", checkin_code: "CHK-XXXXXXXX" }`
    - Code must be valid (15 min before start_at to 15 min after end_at)
    - Changes status from 'active' to 'checkin'
    - Records checkin_at timestamp
  - Body for **checkout**: `{ status: "checkout" }`
    - Changes status from 'checkin' to 'finished'
    - Records checkout_at timestamp
  - Body for **cancel**: `{ status: "cancel" }`
    - Changes status to 'cancelled'
  - Response: `{ success: true, data: {...}, message: "...", status_code: 200 }`

#### Management Endpoints (Protected - Superadmin Only)
- **GET** `/api/bookings/manage` (Superadmin)
  - Get all bookings for management
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ success: true, data: [...], message: "...", status_code: 200 }`
  - Returns bookings with user info (username, email) and floor info

- **GET** `/api/bookings/manage/:id` (Superadmin)
  - Get booking by ID for management
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ success: true, data: {...} }`
  - Returns booking with user info and floor info

- **DELETE** `/api/bookings/manage/:id` (Superadmin)
  - Delete booking (hard delete)
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ success: true, message: "Booking berhasil dihapus", status_code: 200 }`
  - Note: Superadmin can only delete bookings for cleanup purposes. Users own their booking lifecycle (create, checkin, checkout, cancel).

### Statistics (Protected)
- **GET** `/api/stats_employee/:user_id` (Protected)
  - Get employee statistics
  - Headers: `Authorization: Bearer <token>`
  - Response:
    ```json
    {
      "success": true,
      "data": {
        "user_id": 1,
        "today_bookings": 2,
        "upcoming_bookings": 5,
        "weekly_booking_hours": 8.5,
        "favorite_space": {
          "space_id": 3,
          "space_name": "Meeting Room A",
          "space_type": "meeting_room",
          "booking_count": 10
        }
      }
    }
    ```
  - Statistics details:
    - `today_bookings`: Count of active and checkin bookings today
    - `upcoming_bookings`: Count of bookings starting tomorrow or later
    - `weekly_booking_hours`: Total hours from checkin to checkout this week
    - `favorite_space`: Most booked space with booking count

## Database Schema

### Users Table
- `id` - Integer (Primary Key, Auto Increment)
- `username` - String(50, Unique, Nullable=False)
- `email` - String(120, Unique, Nullable=False)
- `password` - String(255, Nullable=False) - Hashed with bcrypt
- `phone` - String(20)
- `role` - String(20, Default='employee') - employee, admin, manager
- `department_id` - Integer (Foreign Key to departments.id)
- `created_at` - DateTime
- `updated_at` - DateTime

### Departments Table
- `id` - Integer (Primary Key)
- `name` - String(100)
- `manager_id` - Integer (Foreign Key to users.id)
- `created_at` - DateTime
- `updated_at` - DateTime

### Floors Table
- `id` - Integer (Primary Key)
- `name` - String(50)
- `level` - Integer
- `created_at` - DateTime
- `updated_at` - DateTime

### Spaces Table
- `id` - Integer (Primary Key)
- `name` - String(100)
- `type` - String(20) - hot_desk, private_room, meeting_room
- `capacity` - Integer
- `location` - Integer (Foreign Key to floors.id)
- `opening_hours` - JSON - {mon: {start: "08:00", end: "18:00"}, ...}
- `max_duration` - Integer (minutes)
- `status` - String(20, Default='available') - available, booked, in_maintenance
- `created_at` - DateTime
- `updated_at` - DateTime

### Amenities Table
- `id` - Integer (Primary Key)
- `space_id` - Integer (Foreign Key to spaces.id)
- `name` - String(50)
- `icon` - String(50)
- `created_at` - DateTime
- `updated_at` - DateTime

### Blackout Dates Table
- `id` - Integer (Primary Key)
- `title` - String(100) - Holiday name
- `start_at` - DateTime
- `end_at` - DateTime
- `created_at` - DateTime
- `updated_at` - DateTime

### Bookings Table
- `id` - Integer (Primary Key)
- `user_id` - Integer (Foreign Key to users.id)
- `space_id` - Integer (Foreign Key to spaces.id)
- `status` - String(20, Default='active') - active, checkin, finished, cancelled
- `start_at` - DateTime
- `end_at` - DateTime
- `max_duration_snapshot` - Integer
- `checkin_code` - String(50, Unique) - CHK-XXXXXXXX
- `code_valid_from` - DateTime - 15 min before start_at
- `code_valid_to` - DateTime - 15 min after end_at
- `checkin_at` - DateTime (Nullable)
- `checkout_at` - DateTime (Nullable)
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
│   │   ├── user.py                 # User model
│   │   ├── department.py           # Department model
│   │   ├── floor.py                # Floor model
│   │   ├── space.py                # Space model
│   │   ├── amenity.py              # Amenity model
│   │   ├── blackout.py             # Blackout date model
│   │   └── booking.py              # Booking model
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── user_repository.py      # User data access layer
│   │   ├── space_repository.py     # Space data access layer
│   │   ├── booking_repository.py   # Booking data access layer
│   │   └── stats_repository.py     # Statistics data access layer
│   ├── usecases/
│   │   ├── __init__.py
│   │   ├── user_usecase.py         # User business logic
│   │   ├── auth_usecase.py         # Authentication business logic
│   │   ├── space_usecase.py        # Space availability logic
│   │   ├── booking_usecase.py      # Booking business logic
│   │   └── stats_usecase.py        # Statistics business logic
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── user_controller.py      # User request handlers
│   │   ├── auth_controller.py      # Auth request handlers
│   │   ├── space_controller.py     # Space request handlers
│   │   ├── booking_controller.py   # Booking request handlers
│   │   ├── stats_controller.py     # Stats request handlers
│   │   └── health_controller.py    # Health check handler
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── user_routes.py          # User endpoint definitions
│   │   ├── auth_routes.py          # Auth endpoint definitions
│   │   ├── space_routes.py         # Space endpoint definitions
│   │   ├── booking_routes.py       # Booking endpoint definitions
│   │   ├── stats_routes.py         # Statistics endpoint definitions
│   │   └── health_routes.py        # Health check endpoint
│   └── utils/
│       ├── __init__.py
│       ├── jwt_helper.py           # JWT token creation and validation
│       ├── response_template.py    # Standardized API responses
│       └── error_handlers.py       # Global error handlers
├── run.py                          # Entry point
├── migrate.py                      # Database migration script
├── seed.py                         # Database seeding script
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
- Authentication decorators (@token_required, @role_required)

### 2. **Controllers** (Presentation Layer)
- Menangani HTTP requests dan responses
- Validasi input dasar
- Memanggil UseCase untuk business logic
- Format response menggunakan ResponseTemplate
- Standardized responses: `{ success: bool, data: any, message: string, status_code: int }`

### 3. **UseCases** (Business Logic Layer)
- Berisi business logic dan rules
- Orchestrate flow data antara controllers dan repositories
- Validasi business rules
- Space availability checking
- Booking conflict detection
- Returns: `{ success: bool, data: any, error: string }`

### 4. **Repositories** (Data Access Layer)
- Menangani semua operasi database
- Abstraksi untuk data persistence
- CRUD operations
- Consistent naming: get_by_id(), get_all_*(), create(), update(), delete()

### 5. **Models** (Entity Layer)
- Definisi struktur data
- Database schema
- Data transformation methods (to_dict())
- Relationships between entities

## Key Features

### Space Availability System
The system implements comprehensive availability checking:

1. **Opening Hours Validation**
   - Stored as JSON per space: `{mon: {start: "08:00", end: "18:00"}, ...}`
   - Day-specific schedules (different hours for each day)
   - Closed days handled (e.g., weekends)

2. **Blackout Dates**
   - System-wide blackout dates (holidays, maintenance)
   - Prevents bookings during blackout periods

3. **Conflict Detection**
   - Checks existing bookings for time overlaps
   - Direct time conflict check (no buffer)
   - Prevents double-booking

4. **Available Hours Calculation**
   - Computes free time slots within opening hours
   - Excludes existing bookings
   - Returns array of available time ranges: `[{start: "HH:MM", end: "HH:MM"}, ...]`

### Booking Workflow

1. **Creation**
   - Validates time order (start < end)
   - Checks not in the past
   - Validates space availability
   - Checks blackout dates
   - Validates opening hours
   - Checks max duration limit
   - Detects conflicts
   - Generates unique checkin code (CHK-XXXXXXXX)
   - Sets code validity window (15 min before to 15 min after)

2. **Check-in**
   - Validates checkin code
   - Checks code validity time window
   - Changes status: active → checkin
   - Records checkin_at timestamp

3. **Checkout**
   - Changes status: checkin → finished
   - Records checkout_at timestamp

4. **Cancellation**
   - Changes status to cancelled
   - Frees up the time slot

### Role-Based Access Control

- **Employee**: Can view spaces, create bookings, check-in/out, cancel own bookings
- **Admin**: Same as employee (future: department management)
- **Manager**: Same as employee (future: department oversight)
- **Superadmin**: Limited management access via `/manage` endpoints:
  - Spaces: View all, update status only
  - Bookings: View all, delete only
  - Users: Full CRUD
  - Departments: Full CRUD

### Management Endpoints

Superadmin-only endpoints with limited administrative access:
- `/api/spaces/manage/*` - View all spaces, update status only (available, booked, in_maintenance)
- `/api/bookings/manage/*` - View all bookings, delete only (cleanup purposes)
- Space creation/deletion managed via seed data
- Users own their booking lifecycle (create, checkin, checkout, cancel)
- Enhanced data with relationships (user info, floor info)

## API Response Format

All endpoints return standardized responses:

**Success:**
```json
{
  "success": true,
  "data": {...} or [...],
  "message": "Operation completed successfully",
  "status_code": 200
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error description",
  "message": "User-friendly error message",
  "status_code": 400
}
```

## Error Handling

Global error handlers for:
- 404 Not Found
- 405 Method Not Allowed
- 500 Internal Server Error
- JWT Authentication Errors
- Validation Errors
- Database Errors

## Development

The application runs in debug mode by default. For production, make sure to:
- Set `SECRET_KEY` to a secure random value
- Set `SQLALCHEMY_ECHO` to `False` in `config.py`
- Use a production WSGI server (gunicorn, uWSGI, etc.)
