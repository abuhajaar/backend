# Docker Setup Guide - OpenBO Backend

Panduan lengkap untuk menjalankan OpenBO Backend menggunakan Docker.

## Prerequisites

- Docker Desktop terinstall
- Docker Compose terinstall (biasanya sudah include di Docker Desktop)

## File Konfigurasi Docker

1. **Dockerfile** - Definisi image untuk aplikasi Flask
2. **docker-compose.yml** - Orchestration untuk multi-container (Flask + MariaDB)
3. **.dockerignore** - File yang diabaikan saat build image
4. **.env.docker** - Template environment variables untuk Docker

## Cara Menjalankan

### 1. Build dan Run dengan Docker Compose

```powershell
# Build dan start semua services
docker-compose up --build

# Atau run di background (detached mode)
docker-compose up -d --build
```

### 2. Akses Aplikasi

- **Backend API**: http://localhost:5000
- **Database**: localhost:3306
  - User: `openbo_user`
  - Password: `openbo_pass`
  - Database: `openbo_db`

### 3. Cek Logs

```powershell
# Lihat logs semua services
docker-compose logs

# Lihat logs backend saja
docker-compose logs backend

# Lihat logs database saja
docker-compose logs db

# Follow logs (real-time)
docker-compose logs -f backend
```

### 4. Stop Services

```powershell
# Stop services
docker-compose stop

# Stop dan remove containers
docker-compose down

# Stop, remove containers, dan hapus volumes (WARNING: data akan hilang)
docker-compose down -v
```

## Konfigurasi Environment Variables

Edit file `docker-compose.yml` pada section `backend.environment`:

```yaml
environment:
  # Database configuration
  DB_HOST: db
  DB_PORT: 3306
  DB_NAME: openbo_db
  DB_USER: openbo_user
  DB_PASSWORD: openbo_pass
  
  # Flask configuration
  FLASK_ENV: production
  SECRET_KEY: ganti-dengan-secret-key-anda-minimal-32-karakter
  
  # Database URL
  DATABASE_URL: mysql+pymysql://openbo_user:openbo_pass@db:3306/openbo_db
```

**PENTING untuk Production:**
- Ganti `SECRET_KEY` dengan random string yang aman
- Ganti password database (`MYSQL_PASSWORD`, `DB_PASSWORD`)
- Gunakan `.env` file untuk menyimpan credentials (lebih aman)

## Menggunakan .env File (Recommended)

1. Copy `.env.docker` ke `.env`:
   ```powershell
   Copy-Item .env.docker .env
   ```

2. Edit `.env` dan ganti values:
   ```
   SECRET_KEY=your-production-secret-key-here
   DB_PASSWORD=your-secure-password
   ```

3. Update `docker-compose.yml` untuk menggunakan `.env`:
   ```yaml
   backend:
     env_file:
       - .env
   ```

## Database Management

### Reset Database

```powershell
# Stop containers
docker-compose down

# Remove database volume
docker volume rm backend_mariadb_data

# Start fresh
docker-compose up --build
```

### Migrate Ulang

```powershell
# Masuk ke container backend
docker-compose exec backend sh

# Di dalam container
python migrate.py
python seed.py
exit
```

### Backup Database

```powershell
# Backup
docker-compose exec db mysqldump -u openbo_user -popenbo_pass openbo_db > backup.sql

# Restore
docker-compose exec -T db mysql -u openbo_user -popenbo_pass openbo_db < backup.sql
```

## Troubleshooting

### Port Already in Use

Jika port 5000 atau 3306 sudah digunakan, edit `docker-compose.yml`:

```yaml
backend:
  ports:
    - "5001:5000"  # Ganti 5001 dengan port yang available

db:
  ports:
    - "3307:3306"  # Ganti 3307 dengan port yang available
```

### Database Connection Error

1. Cek apakah database service healthy:
   ```powershell
   docker-compose ps
   ```

2. Cek logs database:
   ```powershell
   docker-compose logs db
   ```

3. Tunggu beberapa detik lagi, database mungkin masih initializing

### Container Crash Loop

```powershell
# Lihat logs untuk error
docker-compose logs backend

# Rebuild image
docker-compose build --no-cache backend
docker-compose up backend
```

## Commands Berguna

```powershell
# List running containers
docker-compose ps

# Restart service
docker-compose restart backend

# View container resource usage
docker stats

# Clean up unused images
docker image prune

# Remove all stopped containers
docker container prune

# Execute command di container
docker-compose exec backend python --version

# Access backend shell
docker-compose exec backend sh

# Access database shell
docker-compose exec db mysql -u openbo_user -popenbo_pass openbo_db
```

## Production Deployment

Untuk production, tambahkan:

1. **Reverse Proxy (Nginx)**
2. **SSL Certificates**
3. **Proper Secret Management**
4. **Resource Limits**
5. **Health Checks**
6. **Logging & Monitoring**

Contoh dengan Nginx:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
```

## Docker Commands Quick Reference

| Command | Description |
|---------|-------------|
| `docker-compose up` | Start services |
| `docker-compose up -d` | Start in background |
| `docker-compose down` | Stop and remove |
| `docker-compose ps` | List containers |
| `docker-compose logs` | View logs |
| `docker-compose exec <service> <cmd>` | Run command |
| `docker-compose build` | Build images |
| `docker-compose restart` | Restart services |

---

**Need Help?** Check Docker documentation: https://docs.docker.com/
